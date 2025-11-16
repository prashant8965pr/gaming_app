/**
 * Live Game Session Component
 * Real-time game interface with WebSocket integration
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket, WebSocketMessage } from '@/hooks/useWebSocket';
import { useAuthStore } from '@/store/authStore';

interface Player {
  user_id: string;
  username: string;
  position: number;
  score: number;
  status: string;
}

interface GameState {
  moves: Array<{
    user_id: string;
    move: any;
    timestamp: string;
  }>;
  last_move?: {
    user_id: string;
    move: any;
    timestamp: string;
  };
  current_turn?: string;
  [key: string]: any;
}

interface ChatMessage {
  user_id: string;
  username: string;
  message: string;
  timestamp: string;
}

interface LiveGameSessionProps {
  gameSessionId: string;
  onGameEnd?: (results: any) => void;
}

export const LiveGameSession: React.FC<LiveGameSessionProps> = ({
  gameSessionId,
  onGameEnd,
}) => {
  const { user, token } = useAuthStore();

  const [players, setPlayers] = useState<Player[]>([]);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [gameStatus, setGameStatus] = useState<string>('waiting');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [notification, setNotification] = useState<string>('');

  // WebSocket URL
  const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/api/v1/ws/game/${gameSessionId}`;

  // Handle WebSocket messages
  const handleMessage = useCallback(
    (message: WebSocketMessage) => {
      console.log('Received message:', message);

      switch (message.type) {
        case 'connection':
          setNotification('Connected to game session');
          setTimeout(() => setNotification(''), 3000);
          break;

        case 'game_state':
          setPlayers(message.players || []);
          setGameState(message.game_state || {});
          setGameStatus(message.status || 'waiting');
          break;

        case 'game_state_update':
          setGameState(message.state || {});
          break;

        case 'player_joined':
          setNotification(`${message.username} joined the game`);
          setTimeout(() => setNotification(''), 3000);
          break;

        case 'player_left':
          setNotification(`${message.username} left the game`);
          setTimeout(() => setNotification(''), 3000);
          break;

        case 'game_started':
          setGameStatus('in_progress');
          setNotification('Game has started!');
          setTimeout(() => setNotification(''), 3000);
          break;

        case 'game_ended':
          setGameStatus('completed');
          setNotification('Game ended!');
          if (onGameEnd && message.results) {
            onGameEnd(message.results);
          }
          break;

        case 'turn_change':
          setGameState((prev) => ({
            ...prev,
            current_turn: message.next_turn_user_id,
          }));
          if (message.next_turn_user_id === user?.id) {
            setNotification('Your turn!');
            setTimeout(() => setNotification(''), 3000);
          }
          break;

        case 'move_made':
          const playerName =
            players.find((p) => p.user_id === message.user_id)?.username ||
            'Player';
          setNotification(`${playerName} made a move`);
          setTimeout(() => setNotification(''), 2000);
          break;

        case 'chat_message':
          setChatMessages((prev) => [
            ...prev,
            {
              user_id: message.user_id,
              username: message.username,
              message: message.message,
              timestamp: message.timestamp,
            },
          ]);
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    },
    [user?.id, players, onGameEnd]
  );

  // WebSocket connection
  const {
    isConnected,
    connectionState,
    sendMove,
    sendChat,
    requestGameState,
  } = useWebSocket({
    url: wsUrl,
    token: token || undefined,
    onMessage: handleMessage,
    onConnect: () => {
      console.log('Connected to game session');
      // Request initial game state
      requestGameState();
    },
    onDisconnect: () => {
      console.log('Disconnected from game session');
    },
    autoReconnect: true,
    maxReconnectAttempts: 5,
  });

  // Handle chat submit
  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatInput.trim() && isConnected) {
      sendChat(chatInput.trim());
      setChatInput('');
    }
  };

  // Example move handler (customize based on your game logic)
  const handleMove = (moveData: any) => {
    if (isConnected && gameState?.current_turn === user?.id) {
      sendMove(moveData);
    }
  };

  // Check if it's current user's turn
  const isMyTurn = gameState?.current_turn === user?.id;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Connection Status Bar */}
      <div
        className={`px-4 py-2 text-center text-sm font-medium ${
          isConnected
            ? 'bg-green-500 text-white'
            : connectionState === 'connecting'
            ? 'bg-yellow-500 text-white'
            : 'bg-red-500 text-white'
        }`}
      >
        {isConnected
          ? '🟢 Connected'
          : connectionState === 'connecting'
          ? '🟡 Connecting...'
          : '🔴 Disconnected'}
      </div>

      {/* Notification Banner */}
      {notification && (
        <div className="bg-blue-500 text-white px-4 py-3 text-center">
          {notification}
        </div>
      )}

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Game Area */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Live Game Session
                </h1>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    gameStatus === 'in_progress'
                      ? 'bg-green-100 text-green-800'
                      : gameStatus === 'completed'
                      ? 'bg-gray-100 text-gray-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {gameStatus === 'in_progress'
                    ? 'In Progress'
                    : gameStatus === 'completed'
                    ? 'Completed'
                    : 'Waiting'}
                </span>
              </div>

              {/* Players List */}
              <div className="mb-6">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  Players ({players.length})
                </h2>
                <div className="grid grid-cols-2 gap-3">
                  {players.map((player) => (
                    <div
                      key={player.user_id}
                      className={`p-3 rounded-lg border-2 ${
                        player.user_id === user?.id
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700'
                      } ${
                        gameState?.current_turn === player.user_id
                          ? 'ring-2 ring-green-500'
                          : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {player.username}
                          {player.user_id === user?.id && ' (You)'}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          Score: {player.score || 0}
                        </span>
                      </div>
                      {gameState?.current_turn === player.user_id && (
                        <div className="mt-1 text-xs text-green-600 dark:text-green-400 font-medium">
                          🎮 Current Turn
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Game Board / Play Area */}
              <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 min-h-[400px]">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Game Board
                </h2>

                {/* Turn Indicator */}
                {isMyTurn && gameStatus === 'in_progress' && (
                  <div className="mb-4 p-4 bg-green-100 dark:bg-green-900/20 rounded-lg border-2 border-green-500">
                    <p className="text-green-800 dark:text-green-400 font-semibold text-center">
                      🎯 It's your turn! Make your move.
                    </p>
                  </div>
                )}

                {/* Game-specific UI goes here */}
                <div className="text-center text-gray-500 dark:text-gray-400">
                  {/* Replace this with your actual game board */}
                  <p>Game board will be rendered here</p>
                  <p className="text-sm mt-2">
                    Customize this component for your specific game type
                  </p>

                  {/* Example action button */}
                  {isMyTurn && gameStatus === 'in_progress' && (
                    <button
                      onClick={() => handleMove({ action: 'example' })}
                      className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                      Make Move
                    </button>
                  )}
                </div>

                {/* Move History */}
                {gameState?.moves && gameState.moves.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Move History
                    </h3>
                    <div className="space-y-1 max-h-32 overflow-y-auto">
                      {gameState.moves.slice(-5).map((move, index) => (
                        <div
                          key={index}
                          className="text-xs text-gray-600 dark:text-gray-400"
                        >
                          {players.find((p) => p.user_id === move.user_id)
                            ?.username || 'Player'}{' '}
                          made a move
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Chat Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 h-[600px] flex flex-col">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Chat
              </h2>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto mb-4 space-y-2">
                {chatMessages.map((msg, index) => (
                  <div
                    key={index}
                    className={`p-2 rounded-lg ${
                      msg.user_id === user?.id
                        ? 'bg-blue-100 dark:bg-blue-900/20 ml-8'
                        : 'bg-gray-100 dark:bg-gray-700 mr-8'
                    }`}
                  >
                    <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">
                      {msg.username}
                      {msg.user_id === user?.id && ' (You)'}
                    </div>
                    <div className="text-sm text-gray-900 dark:text-white mt-1">
                      {msg.message}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>

              {/* Chat Input */}
              <form onSubmit={handleChatSubmit} className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type a message..."
                  disabled={!isConnected}
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={!isConnected || !chatInput.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Send
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveGameSession;
