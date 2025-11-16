import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../data/models/game_model.dart';
import '../../bloc/game/game_bloc.dart';
import '../../bloc/game/game_event.dart';
import '../../bloc/game/game_state.dart';
import '../../widgets/game_card.dart';
import '../../widgets/loading_indicator.dart';
import '../../widgets/error_widget.dart';
import '../../widgets/empty_state.dart';
import '../game/game_details_screen.dart';

/// Games browse screen with search and filter
class GamesBrowseScreen extends StatefulWidget {
  const GamesBrowseScreen({super.key});

  @override
  State<GamesBrowseScreen> createState() => _GamesBrowseScreenState();
}

class _GamesBrowseScreenState extends State<GamesBrowseScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  String _searchQuery = '';
  String _selectedCategory = 'all';
  String _selectedDifficulty = 'all';
  bool _showOnlyActive = false;

  final List<Map<String, dynamic>> _categories = [
    {'id': 'all', 'name': 'All', 'icon': Icons.apps},
    {'id': 'card', 'name': 'Card Games', 'icon': Icons.style},
    {'id': 'board', 'name': 'Board Games', 'icon': Icons.dashboard},
    {'id': 'sports', 'name': 'Sports', 'icon': Icons.sports_cricket},
    {'id': 'quiz', 'name': 'Quiz', 'icon': Icons.quiz},
    {'id': 'puzzle', 'name': 'Puzzle', 'icon': Icons.extension},
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadGames();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _loadGames() {
    context.read<GameBloc>().add(const LoadGamesEvent());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _onRefresh,
          child: Column(
            children: [
              // App Bar
              _buildAppBar(),

              // Search Bar
              _buildSearchBar(),

              // Category Filters
              _buildCategoryFilters(),

              // Tabs
              _buildTabBar(),

              // Games Grid
              Expanded(child: _buildGamesGrid()),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showFilters,
        icon: const Icon(Icons.filter_list),
        label: const Text('Filters'),
        backgroundColor: AppColors.primary,
      ),
    );
  }

  Widget _buildAppBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.white,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Explore Games',
                  style: AppTextStyles.heading2,
                ),
                Text(
                  'Find your favorite games',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.search),
            onPressed: () {
              // Focus on search bar
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.white,
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: 'Search games...',
          prefixIcon: const Icon(Icons.search),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear),
                  onPressed: () {
                    _searchController.clear();
                    setState(() {
                      _searchQuery = '';
                    });
                  },
                )
              : null,
          filled: true,
          fillColor: AppColors.background,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 12,
          ),
        ),
        onChanged: (value) {
          setState(() {
            _searchQuery = value.toLowerCase();
          });
        },
      ),
    );
  }

  Widget _buildCategoryFilters() {
    return Container(
      height: 80,
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        itemCount: _categories.length,
        itemBuilder: (context, index) {
          final category = _categories[index];
          final isSelected = _selectedCategory == category['id'];

          return GestureDetector(
            onTap: () {
              setState(() {
                _selectedCategory = category['id'] as String;
              });
            },
            child: Container(
              width: 100,
              margin: const EdgeInsets.symmetric(horizontal: 4),
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.primary : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isSelected ? AppColors.primary : Colors.grey.shade300,
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    category['icon'] as IconData,
                    color: isSelected ? Colors.white : AppColors.textSecondary,
                    size: 24,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    category['name'] as String,
                    style: AppTextStyles.caption.copyWith(
                      color: isSelected ? Colors.white : AppColors.textSecondary,
                      fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
      ),
      child: TabBar(
        controller: _tabController,
        labelColor: AppColors.primary,
        unselectedLabelColor: AppColors.textSecondary,
        indicatorColor: AppColors.primary,
        indicatorWeight: 3,
        onTap: (index) {
          setState(() {}); // Rebuild to apply filter
        },
        tabs: const [
          Tab(text: 'All'),
          Tab(text: 'Popular'),
          Tab(text: 'New'),
        ],
      ),
    );
  }

  Widget _buildGamesGrid() {
    return BlocBuilder<GameBloc, GameState>(
      builder: (context, state) {
        if (state is GameLoading) {
          return const Center(child: LoadingIndicator());
        }

        if (state is GameError) {
          return ErrorDisplay(
            message: state.message,
            onRetry: _loadGames,
          );
        }

        if (state is GamesLoaded) {
          if (state.games.isEmpty) {
            return const NoGamesAvailable();
          }

          // Apply filters
          final filteredGames = _filterGames(state.games);

          if (filteredGames.isEmpty) {
            return EmptyState(
              title: 'No Games Found',
              message: _searchQuery.isNotEmpty
                  ? 'No games match your search "$_searchQuery"'
                  : 'No games available in this category.',
              icon: Icons.search_off,
              actionText: 'Clear Filters',
              onAction: () {
                setState(() {
                  _searchQuery = '';
                  _selectedCategory = 'all';
                  _selectedDifficulty = 'all';
                  _showOnlyActive = false;
                  _searchController.clear();
                  _tabController.index = 0;
                });
              },
            );
          }

          return GridView.builder(
            padding: const EdgeInsets.all(16),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              childAspectRatio: 0.75,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemCount: filteredGames.length,
            itemBuilder: (context, index) {
              final game = filteredGames[index];
              return _buildGameGridCard(game);
            },
          );
        }

        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.games,
                size: 64,
                color: AppColors.textHint,
              ),
              const SizedBox(height: 16),
              Text(
                'Load games to get started',
                style: AppTextStyles.body.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildGameGridCard(GameModel game) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => GameDetailsScreen(gameId: game.id),
          ),
        );
      },
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Game thumbnail
            Stack(
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(16),
                  ),
                  child: AspectRatio(
                    aspectRatio: 1.2,
                    child: game.thumbnailUrl != null
                        ? Image.network(
                            game.thumbnailUrl!,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                color: AppColors.primary.withOpacity(0.1),
                                child: const Icon(
                                  Icons.games,
                                  size: 48,
                                  color: AppColors.primary,
                                ),
                              );
                            },
                          )
                        : Container(
                            color: AppColors.primary.withOpacity(0.1),
                            child: const Icon(
                              Icons.games,
                              size: 48,
                              color: AppColors.primary,
                            ),
                          ),
                  ),
                ),
                // Status badge
                if (game.status == 'active')
                  Positioned(
                    top: 8,
                    right: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.success,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'LIVE',
                        style: AppTextStyles.caption.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 10,
                        ),
                      ),
                    ),
                  ),
              ],
            ),

            // Game info
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      game.name,
                      style: AppTextStyles.bodyBold,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    if (game.description != null)
                      Text(
                        game.description!,
                        style: AppTextStyles.caption.copyWith(
                          color: AppColors.textSecondary,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    const Spacer(),
                    Row(
                      children: [
                        Icon(
                          Icons.people_outline,
                          size: 14,
                          color: AppColors.textSecondary,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${game.minPlayers}-${game.maxPlayers}',
                          style: AppTextStyles.caption.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        const Spacer(),
                        if (game.isPopular ?? false)
                          const Icon(
                            Icons.trending_up,
                            size: 14,
                            color: AppColors.warning,
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<GameModel> _filterGames(List<GameModel> games) {
    var filtered = games;

    // Filter by search query
    if (_searchQuery.isNotEmpty) {
      filtered = filtered.where((game) {
        return game.name.toLowerCase().contains(_searchQuery) ||
            (game.description?.toLowerCase().contains(_searchQuery) ?? false);
      }).toList();
    }

    // Filter by category
    if (_selectedCategory != 'all') {
      filtered = filtered.where((game) {
        return game.gameType == _selectedCategory;
      }).toList();
    }

    // Filter by difficulty
    if (_selectedDifficulty != 'all') {
      filtered = filtered.where((game) {
        return game.difficulty == _selectedDifficulty;
      }).toList();
    }

    // Filter by active status
    if (_showOnlyActive) {
      filtered = filtered.where((game) {
        return game.status == 'active';
      }).toList();
    }

    // Apply tab filter
    final tabIndex = _tabController.index;
    if (tabIndex == 1) {
      // Popular
      filtered = filtered.where((game) {
        return game.isPopular ?? false;
      }).toList();
    } else if (tabIndex == 2) {
      // New - sort by created date
      filtered.sort((a, b) => b.createdAt.compareTo(a.createdAt));
      filtered = filtered.take(10).toList();
    }

    return filtered;
  }

  void _showFilters() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) {
          return Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  children: [
                    Text(
                      'Filters',
                      style: AppTextStyles.heading3,
                    ),
                    const Spacer(),
                    TextButton(
                      onPressed: () {
                        setModalState(() {
                          _selectedDifficulty = 'all';
                          _showOnlyActive = false;
                        });
                        setState(() {
                          _selectedDifficulty = 'all';
                          _showOnlyActive = false;
                        });
                      },
                      child: const Text('Reset'),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Difficulty filter
                Text(
                  'Difficulty',
                  style: AppTextStyles.bodyMedium,
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  children: [
                    _buildFilterChip(
                      'All',
                      _selectedDifficulty == 'all',
                      () {
                        setModalState(() => _selectedDifficulty = 'all');
                        setState(() => _selectedDifficulty = 'all');
                      },
                    ),
                    _buildFilterChip(
                      'Easy',
                      _selectedDifficulty == 'easy',
                      () {
                        setModalState(() => _selectedDifficulty = 'easy');
                        setState(() => _selectedDifficulty = 'easy');
                      },
                    ),
                    _buildFilterChip(
                      'Medium',
                      _selectedDifficulty == 'medium',
                      () {
                        setModalState(() => _selectedDifficulty = 'medium');
                        setState(() => _selectedDifficulty = 'medium');
                      },
                    ),
                    _buildFilterChip(
                      'Hard',
                      _selectedDifficulty == 'hard',
                      () {
                        setModalState(() => _selectedDifficulty = 'hard');
                        setState(() => _selectedDifficulty = 'hard');
                      },
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                // Show only active
                SwitchListTile(
                  title: const Text('Show only active games'),
                  value: _showOnlyActive,
                  onChanged: (value) {
                    setModalState(() => _showOnlyActive = value);
                    setState(() => _showOnlyActive = value);
                  },
                  activeColor: AppColors.primary,
                ),

                const SizedBox(height: 24),

                // Apply button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text('Apply Filters'),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildFilterChip(String label, bool isSelected, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? AppColors.primary : Colors.grey.shade300,
          ),
        ),
        child: Text(
          label,
          style: AppTextStyles.body.copyWith(
            color: isSelected ? Colors.white : AppColors.textPrimary,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
      ),
    );
  }

  Future<void> _onRefresh() async {
    context.read<GameBloc>().add(const LoadGamesEvent());
  }
}
