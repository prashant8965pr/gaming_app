/**
 * Achievements Page
 */

'use client';

import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Trophy, Lock, CheckCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge, Spinner, EmptyState } from '@/components/common';
import { formatCurrency } from '@/utils/format';
import { api } from '@/lib/api';
import type { Achievement, UserAchievement } from '@/types';

export default function AchievementsPage() {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [userAchievements, setUserAchievements] = useState<Map<string, UserAchievement>>(new Map());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadAchievements();
  }, []);

  const loadAchievements = async () => {
    try {
      const data = await api.getAchievements();
      setAchievements(data);

      // Create map of user achievements
      const userAchMap = new Map();
      data.forEach((achievement: any) => {
        if (achievement.user_achievement) {
          userAchMap.set(achievement.id, achievement.user_achievement);
        }
      });
      setUserAchievements(userAchMap);
    } catch (error) {
      console.error('Failed to load achievements:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClaim = async (achievementId: string) => {
    try {
      await api.claimAchievement(achievementId);
      toast.success('Achievement claimed!');
      loadAchievements();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to claim achievement';
      toast.error(message);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Spinner size="lg" />
      </div>
    );
  }

  const categories = Array.from(new Set(achievements.map((a) => a.category)));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Achievements</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Complete challenges and earn rewards
        </p>
      </div>

      {categories.map((category) => {
        const categoryAchievements = achievements.filter((a) => a.category === category);

        return (
          <div key={category}>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 capitalize">
              {category}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categoryAchievements.map((achievement) => {
                const userAch = userAchievements.get(achievement.id);
                const isCompleted = userAch?.progress === 100;
                const isClaimed = userAch?.is_claimed;

                return (
                  <AchievementCard
                    key={achievement.id}
                    achievement={achievement}
                    progress={userAch?.progress || 0}
                    isCompleted={isCompleted}
                    isClaimed={isClaimed}
                    onClaim={() => handleClaim(achievement.id)}
                  />
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

interface AchievementCardProps {
  achievement: Achievement;
  progress: number;
  isCompleted?: boolean;
  isClaimed?: boolean;
  onClaim: () => void;
}

function AchievementCard({ achievement, progress, isCompleted, isClaimed, onClaim }: AchievementCardProps) {
  return (
    <Card className={isCompleted ? 'border-2 border-success-500' : ''}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className={`p-3 rounded-lg ${isCompleted ? 'bg-success-100 text-success-600' : 'bg-gray-100 text-gray-400'}`}>
            {isCompleted ? <Trophy className="w-6 h-6" /> : <Lock className="w-6 h-6" />}
          </div>
          {isClaimed && <Badge variant="success">Claimed</Badge>}
        </div>

        <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
          {achievement.name}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
          {achievement.description}
        </p>

        {/* Progress Bar */}
        <div className="mb-3">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Progress</span>
            <span className="text-gray-900 dark:text-white font-medium">{progress}%</span>
          </div>
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-success-500 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Rewards */}
        <div className="flex items-center justify-between text-sm mb-3">
          <span className="text-gray-600 dark:text-gray-400">Rewards:</span>
          <div className="flex gap-2">
            {achievement.xp_reward > 0 && (
              <Badge variant="info">{achievement.xp_reward} XP</Badge>
            )}
            {achievement.bonus_reward > 0 && (
              <Badge variant="success">{formatCurrency(achievement.bonus_reward)}</Badge>
            )}
          </div>
        </div>

        {/* Claim Button */}
        {isCompleted && !isClaimed && (
          <Button onClick={onClaim} size="sm" className="w-full">
            Claim Reward
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
