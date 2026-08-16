'use client';

import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

import ChatInterface from '@/components/ChatInterface';
import LiveBrowserView from '@/components/LiveBrowserView';
import TaskStatusBar from '@/components/TaskStatusBar';

export default function Workspace() {
  const [agentState, setAgentState] = useState('idle');
  const [vncUrl, setVncUrl] = useState('');

  return (
    <main className="min-h-screen bg-bg-pure text-gray-100 font-sans selection:bg-purple-500/30">

      {/* Ambient Background Glow */}
      <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-purple-900/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="fixed bottom-0 right-1/4 w-[500px] h-[500px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10 flex flex-col h-screen p-4 gap-4">

        <header className="flex items-center justify-between px-4 py-3 rounded-2xl border border-glass-border bg-bg-panel backdrop-blur-md">

          <div className="flex items-center gap-3">

            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-slow" />

            <h1 className="text-sm font-medium tracking-wide text-gray-300">
              Agent Workspace
            </h1>

          </div>

          <TaskStatusBar state={agentState} />

        </header>

        <div className="flex-1 flex flex-col lg:flex-row gap-4 overflow-hidden">

          {/* Left: Chat & Controls */}

          <div className="w-full lg:w-[400px] flex flex-col rounded-2xl border border-glass-border bg-bg-panel backdrop-blur-md">

            <ChatInterface
              onStateChange={setAgentState}
              onVncConnect={setVncUrl}
            />

          </div>

          {/* Right: Live Browser */}

          <div className="flex-1 relative rounded-2xl overflow-hidden border border-glass-border bg-black shadow-2xl">

            <AnimatePresence mode="wait">

              {vncUrl ? (

                <LiveBrowserView
                  url={vncUrl}
                  state={agentState}
                />

              ) : (

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 flex items-center justify-center"
                >

                  <p className="text-gray-500 text-sm">
                    Browser will initialize when task starts
                  </p>

                </motion.div>

              )}

            </AnimatePresence>

          </div>

        </div>

      </div>

    </main>
  );
}
