/**
 * Leaderboard Page
 */

'use client';

import { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Medal } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Avatar, Badge, Spinner } from '@/components/common';
import { formatCurrency } from '@/utils/format';
import { api } from '@/lib/api';
import type { LeaderboardEntry } from '@/types';

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [myRank, setMyRank] = useState<any>(null);
  const [period, setPeriod] = useState<'daily' | 'weekly' | 'monthly' | 'all_time'>('all_time');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
    loadMyRank();
  }, [period]);

  const loadLeaderboard = async () => {
    try {
      const data = await api.getLeaderboard(period, 100);
      setLeaderboard(data);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMyRank = async () => {
    try {
      const data = await api.getMyRank();
      setMyRank(data);
    } catch (error) {
      console.error('Failed to load rank:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Leaderboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          See how you rank against other players
        </p>
      </div>

      {/* Period Selector */}
      <div className="flex gap-2 overflow-x-auto">
        {(['daily', 'weekly', 'monthly', 'all_time'] as const).map((p) => (
          <Button
            key={p}
            variant={period === p ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setPeriod(p)}
          >
            {p.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
          </Button>
        ))}
      </div>

      {/* My Rank */}
      {myRank && (
        <Card variant="elevated">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Avatar name={myRank.username} size="lg" />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    Your Rank
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {myRank.username}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-primary-600">#{myRank.rank}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {myRank.score} points
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Leaderboard List */}
      <Card>
        <CardHeader>
          <CardTitle>Top Players</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {leaderboard.map((entry, index) => (
              <LeaderboardRow key={entry.user_id} entry={entry} rank={index + 1} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function LeaderboardRow({ entry, rank }: { entry: LeaderboardEntry; rank: number }) {
  const getMedalIcon = () => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Medal className="w-6 h-6 text-orange-600" />;
    return null;
  };

  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800">
      <div className="flex items-center gap-4">
        <div className="w-12 text-center">
          {getMedalIcon() || (
            <span className="text-xl font-bold text-gray-500">#{rank}</span>
          )}
        </div>
        <Avatar name={entry.username} src={entry.avatar_url} size="md" />
        <div>
          <p className="font-medium text-gray-900 dark:text-white">{entry.username}</p>
          <div className="flex gap-3 text-sm text-gray-600 dark:text-gray-400">
            <span>{entry.games_played} games</span>
            <span>{entry.win_rate.toFixed(1)}% win rate</span>
          </div>
        </div>
      </div>
      <div className="text-right">
        <p className="text-lg font-bold text-gray-900 dark:text-white">
          {entry.score}
        </p>
        <p className="text-sm text-gray-600 dark:text-gray-400">points</p>
      </div>
    </div>
  );
}
