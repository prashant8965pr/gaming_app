/**
 * Game Details & Lobby Page
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import { Play, Users, Trophy, Clock, Plus } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Spinner, Alert, Modal, ModalFooter, Input } from '@/components/common';
import { useForm } from 'react-hook-form';
import { formatCurrency, formatRelativeDate } from '@/utils/format';
import { api } from '@/lib/api';
import type { Game, GameSession, CreateSessionRequest } from '@/types';

export default function GameDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const gameId = params.gameId as string;

  const [game, setGame] = useState<Game | null>(null);
  const [sessions, setSessions] = useState<GameSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    if (gameId) {
      loadGameDetails();
      loadSessions();
    }
  }, [gameId]);

  const loadGameDetails = async () => {
    try {
      const data = await api.getGame(gameId);
      setGame(data);
    } catch (error) {
      console.error('Failed to load game:', error);
      toast.error('Game not found');
      router.push('/games');
    }
  };

  const loadSessions = async () => {
    try {
      const data = await api.getGameSessions('waiting');
      // Filter sessions for this game
      const gameSessions = data.filter((s: any) => s.game_id === gameId);
      setSessions(gameSessions);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinSession = async (sessionCode: string) => {
    try {
      await api.joinGameSession({ session_code: sessionCode });
      toast.success('Joined session successfully!');
      router.push(`/games/session/${sessionCode}`);
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to join session';
      toast.error(message);
    }
  };

  if (isLoading || !game) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Game Header */}
      <div className="relative h-64 rounded-lg overflow-hidden bg-gradient-to-br from-primary-600 to-primary-800">
        {game.thumbnail_url && (
          <img
            src={game.thumbnail_url}
            alt={game.name}
            className="w-full h-full object-cover opacity-50"
          />
        )}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-white">
            <h1 className="text-4xl font-bold mb-2">{game.name}</h1>
            <p className="text-xl text-primary-100">{game.description}</p>
          </div>
        </div>
      </div>

      {/* Game Info */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <InfoCard
          icon={<Trophy className="w-6 h-6" />}
          label="Entry Fee"
          value={`${formatCurrency(game.min_entry_fee)} - ${formatCurrency(game.max_entry_fee)}`}
        />
        <InfoCard
          icon={<Users className="w-6 h-6" />}
          label="Players"
          value={`${game.min_players}-${game.max_players}`}
        />
        <InfoCard
          icon={<Badge className="w-6 h-6" />}
          label="Category"
          value={game.category}
        />
        <InfoCard
          icon={<Play className="w-6 h-6" />}
          label="Status"
          value={game.is_active ? 'Active' : 'Inactive'}
        />
      </div>

      {/* Available Sessions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Available Sessions</CardTitle>
          <Button
            onClick={() => setShowCreateModal(true)}
            leftIcon={<Plus className="w-4 h-4" />}
          >
            Create Session
          </Button>
        </CardHeader>
        <CardContent>
          {sessions.length > 0 ? (
            <div className="space-y-3">
              {sessions.map((session) => (
                <SessionCard
                  key={session.id}
                  session={session}
                  onJoin={() => handleJoinSession(session.session_code)}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">No active sessions available</p>
              <Button onClick={() => setShowCreateModal(true)}>
                Create First Session
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Session Modal */}
      <CreateSessionModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        game={game}
        onSuccess={() => {
          setShowCreateModal(false);
          loadSessions();
        }}
      />
    </div>
  );
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3">
        <div className="p-3 bg-primary-100 dark:bg-primary-900/20 text-primary-600 rounded-lg">
          {icon}
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="font-semibold text-gray-900 dark:text-white">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

function SessionCard({ session, onJoin }: { session: GameSession; onJoin: () => void }) {
  return (
    <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <p className="font-medium text-gray-900 dark:text-white">
              Session #{session.session_code}
            </p>
            <Badge variant={session.is_private ? 'warning' : 'info'}>
              {session.is_private ? 'Private' : 'Public'}
            </Badge>
            <Badge variant="success">{session.status}</Badge>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
            <span>Entry: {formatCurrency(session.entry_fee)}</span>
            <span>Prize Pool: {formatCurrency(session.prize_pool)}</span>
            <span>Players: {session.current_players}/{session.max_players}</span>
          </div>
        </div>
        <Button onClick={onJoin}>Join</Button>
      </div>
    </div>
  );
}

interface CreateSessionModalProps {
  isOpen: boolean;
  onClose: () => void;
  game: Game;
  onSuccess: () => void;
}

function CreateSessionModal({ isOpen, onClose, game, onSuccess }: CreateSessionModalProps) {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateSessionRequest>();

  const onSubmit = async (data: CreateSessionRequest) => {
    setIsLoading(true);

    try {
      const payload = {
        ...data,
        game_id: game.id,
        session_type: 'public',
      };

      await api.createGameSession(payload);
      toast.success('Session created successfully!');
      reset();
      onSuccess();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to create session';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Game Session" size="md">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Alert variant="info">
          Creating a session for {game.name}
        </Alert>

        <Input
          label="Entry Fee"
          type="number"
          placeholder={`${game.min_entry_fee} - ${game.max_entry_fee}`}
          error={errors.entry_fee?.message}
          {...register('entry_fee', {
            required: 'Entry fee is required',
            min: { value: game.min_entry_fee, message: `Minimum Rs.${game.min_entry_fee}` },
            max: { value: game.max_entry_fee, message: `Maximum Rs.${game.max_entry_fee}` },
          })}
        />

        <Input
          label="Maximum Players"
          type="number"
          placeholder={`${game.min_players} - ${game.max_players}`}
          error={errors.max_players?.message}
          {...register('max_players', {
            required: 'Maximum players is required',
            min: { value: game.min_players, message: `Minimum ${game.min_players} players` },
            max: { value: game.max_players, message: `Maximum ${game.max_players} players` },
          })}
        />

        <div className="flex items-center">
          <input type="checkbox" className="mr-2" {...register('is_private')} />
          <label className="text-sm text-gray-700 dark:text-gray-300">
            Make this a private session
          </label>
        </div>

        <ModalFooter>
          <Button variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isLoading}>
            Create & Join
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
}
