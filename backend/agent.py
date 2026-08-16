import asyncio
import json
import os
from playwright.async_api import async_playwright
import google.generativeai as genai


class BrowserAgent:
    def __init__(self, ws_manager, api_key):
        self.ws = ws_manager
        self.api_key = api_key
        self.browser = None
        self.page = None
        self.playwright = None
        self.paused_for_human = False

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    async def start_session(self):
        self.playwright = await async_playwright().start()

        # Launch inside the Xvfb display
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox"],
        )

        context = await self.browser.new_context(
            viewport={"width": 1280, "height": 1024},
            accept_downloads=True,
        )

        self.page = await context.new_page()

    async def get_page_state(self):
        """Extracts a clean accessibility tree rather than a massive raw DOM."""
        try:
            tree = await self.page.accessibility.snapshot(interesting_only=True)

            return {
                "url": self.page.url,
                "title": await self.page.title(),
                "accessibility_tree": tree,
            }

        except Exception:
            return {
                "url": self.page.url,
                "error": "Page loading",
            }

    async def check_for_human_intervention(self):
        """Detects CAPTCHAs and Cloudflare challenges."""
        try:
            cf_challenge = await self.page.query_selector("#challenge-running")
            recaptcha = await self.page.query_selector(
                'iframe[src*="recaptcha"]'
            )
            hcaptcha = await self.page.query_selector(
                'iframe[src*="hcaptcha"]'
            )

            if (
                cf_challenge
                or recaptcha
                or hcaptcha
                or "Just a moment" in await self.page.title()
            ):
                return True

        except Exception:
            pass

        return False

    async def run_loop(self, user_prompt):
        await self.send_status(
            "understanding",
            "Analyzing your request...",
        )

        history = [
            {
                "role": "user",
                "parts": [
                    {
                        "text": user_prompt
                    }
                ],
            }
        ]

        tools = {
            "function_declarations": [
                {
                    "name": "navigate",
                    "description": "Navigate to a URL",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "url": {
                                "type": "STRING"
                            }
                        },
                    },
                },
                {
                    "name": "click",
                    "description": "Click an element using a descriptive label or accessibility path",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "selector": {
                                "type": "STRING"
                            }
                        },
                    },
                },
                {
                    "name": "type",
                    "description": "Type text into an input field",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "selector": {
                                "type": "STRING"
                            },
                            "text": {
                                "type": "STRING"
                            },
                        },
                    },
                },
                {
                    "name": "wait",
                    "description": "Wait for a specific element or network state",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "selector": {
                                "type": "STRING"
                            }
                        },
                    },
                },
                {
                    "name": "finish_task",
                    "description": "Call this when the user's objective is fully achieved",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "summary": {
                                "type": "STRING"
                            }
                        },
                    },
                },
                {
                    "name": "human_intervention",
                    "description": "Call this if you are stuck on a CAPTCHA or MFA",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "instruction": {
                                "type": "STRING"
                            }
                        },
                    },
                },
            ]
        }

        for step in range(25):
            if self.paused_for_human:
                await asyncio.sleep(2)

                if not await self.check_for_human_intervention():
                    self.paused_for_human = False

                    await self.send_status(
                        "resuming",
                        "Security check passed. Resuming...",
                    )

                continue

            state = await self.get_page_state()

            system_prompt = f"""
You are an expert AI browser operator.

Current URL:
{state['url']}

Page Title:
{state['title']}

Accessibility Tree:
{json.dumps(state.get('accessibility_tree', {}))}

Determine the next action.

Do NOT guess selectors.

If a page changes, re-evaluate.

If you see a CAPTCHA or MFA, call 'human_intervention'.

If the final goal is achieved, call 'finish_task'.
"""

            response = await self.model.generate_content_async(
                [system_prompt] + history,
                generation_config={
                    "tools": [
                        {
                            "function_declarations": tools[
                                "function_declarations"
                            ]
                        }
                    ]
                },
            )

            decision = self.parse_gemini_response(response)

            await self.send_status(
                "thinking",
                decision.get(
                    "reasoning",
                    "Deciding next step...",
                ),
            )

            if decision["action"] == "finish_task":
                await self.send_status(
                    "completed",
                    decision.get(
                        "summary",
                        "Task completed.",
                    ),
                )
                break

            elif decision["action"] == "human_intervention":
                self.paused_for_human = True

                await self.send_status(
                    "intervention",
                    "Human verification required. Please interact with the live browser.",
                )

                continue

            await self.execute_action(decision)

            await asyncio.sleep(2)

            history.append(
                {
                    "role": "model",
                    "parts": [
                        {
                            "function_call": decision
                        }
                    ],
                }
            )

    async def execute_action(self, action):
        await self.send_status(
            "acting",
            f"Executing: {action['action']}...",
        )

        try:
            if action["action"] == "navigate":
                await self.page.goto(
                    action["url"],
                    wait_until="domcontentloaded",
                )

            elif action["action"] == "click":
                await self.page.click(
                    action["selector"],
                    timeout=10000,
                )

            elif action["action"] == "type":
                await self.page.fill(
                    action["selector"],
                    action["text"],
                )

            elif action["action"] == "wait":
                await self.page.wait_for_selector(
                    action["selector"],
                    timeout=15000,
                )

        except Exception:
            pass

    async def send_status(self, state, message):
        await self.ws.send_json(
            {
                "type": "status",
                "state": state,
                "message": message,
            }
                )
