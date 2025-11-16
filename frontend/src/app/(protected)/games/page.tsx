/**
 * Games Catalog Page
 */

'use client';

import { useState, useEffect } from 'react';
import { Search, Filter, Play } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, Button, Input, Badge, Spinner, EmptyState } from '@/components/common';
import { formatCurrency } from '@/utils/format';
import { api } from '@/lib/api';
import type { Game } from '@/types';

export default function GamesPage() {
  const router = useRouter();
  const [games, setGames] = useState<Game[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    loadGames();
  }, []);

  const loadGames = async () => {
    try {
      const data = await api.getGameCatalog();
      setGames(data);
    } catch (error) {
      console.error('Failed to load games:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredGames = games.filter((game) => {
    const matchesSearch = game.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         game.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || game.category === selectedCategory;
    return matchesSearch && matchesCategory && game.is_active;
  });

  const categories = ['all', ...Array.from(new Set(games.map((g) => g.category)))];

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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Browse Games</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Choose your game and start winning
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="Search games..."
            leftIcon={<Search className="w-5 h-5" />}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(category)}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Games Grid */}
      {filteredGames.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredGames.map((game) => (
            <GameCard
              key={game.id}
              game={game}
              onPlay={() => router.push(`/games/${game.id}`)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Search className="w-16 h-16" />}
          title="No games found"
          description="Try adjusting your search or filter"
        />
      )}
    </div>
  );
}

interface GameCardProps {
  game: Game;
  onPlay: () => void;
}

function GameCard({ game, onPlay }: GameCardProps) {
  return (
    <Card hover className="overflow-hidden">
      <div className="relative h-48 bg-gradient-to-br from-primary-400 to-primary-600">
        {game.thumbnail_url ? (
          <img
            src={game.thumbnail_url}
            alt={game.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <Play className="w-16 h-16 text-white opacity-50" />
          </div>
        )}
        <div className="absolute top-3 right-3">
          <Badge variant="success">{game.category}</Badge>
        </div>
      </div>
      <CardContent className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {game.name}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
          {game.description}
        </p>
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-xs text-gray-500">Entry Fee</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">
              {formatCurrency(game.min_entry_fee)} - {formatCurrency(game.max_entry_fee)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Players</p>
            <p className="text-sm font-semibold text-gray-900 dark:text-white">
              {game.min_players}-{game.max_players}
            </p>
          </div>
        </div>
        <Button onClick={onPlay} className="w-full" leftIcon={<Play className="w-4 h-4" />}>
          Play Now
        </Button>
      </CardContent>
    </Card>
  );
}
