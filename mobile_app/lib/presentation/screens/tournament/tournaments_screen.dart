import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../bloc/tournament/tournament_bloc.dart';
import '../../bloc/tournament/tournament_event.dart';
import '../../bloc/tournament/tournament_state.dart';
import '../../widgets/tournament_card.dart';
import '../../../data/models/tournament_model.dart';

class TournamentsScreen extends StatefulWidget {
  const TournamentsScreen({Key? key}) : super(key: key);

  @override
  State<TournamentsScreen> createState() => _TournamentsScreenState();
}

class _TournamentsScreenState extends State<TournamentsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadTournaments();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _loadTournaments() {
    context.read<TournamentBloc>().add(const LoadTournaments(refresh: true));
  }

  void _onTabChanged() {
    String? status;
    switch (_tabController.index) {
      case 0: // All
        status = null;
        break;
      case 1: // Upcoming
        status = 'upcoming';
        break;
      case 2: // Live
        status = 'in_progress';
        break;
      case 3: // Completed
        status = 'completed';
        break;
    }

    context.read<TournamentBloc>().add(LoadTournaments(
          status: status,
          refresh: true,
        ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tournaments'),
        bottom: TabBar(
          controller: _tabController,
          onTap: (_) => _onTabChanged(),
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Upcoming'),
            Tab(text: 'Live'),
            Tab(text: 'Completed'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.emoji_events),
            onPressed: () {
              Navigator.pushNamed(context, '/my-tournaments');
            },
            tooltip: 'My Tournaments',
          ),
        ],
      ),
      body: BlocConsumer<TournamentBloc, TournamentState>(
        listener: (context, state) {
          if (state is TournamentError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message)),
            );
          }
        },
        builder: (context, state) {
          if (state is TournamentLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state is TournamentLoaded) {
            if (state.tournaments.isEmpty) {
              return _buildEmptyState();
            }

            return RefreshIndicator(
              onRefresh: () async {
                _onTabChanged();
              },
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: state.tournaments.length,
                itemBuilder: (context, index) {
                  final tournament = state.tournaments[index];
                  return TournamentCard(
                    tournament: tournament,
                    onTap: () => _navigateToDetails(tournament),
                  );
                },
              ),
            );
          }

          return _buildEmptyState();
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.emoji_events,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No tournaments available',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: _loadTournaments,
            child: const Text('Refresh'),
          ),
        ],
      ),
    );
  }

  void _navigateToDetails(TournamentModel tournament) {
    Navigator.pushNamed(
      context,
      '/tournament-details',
      arguments: tournament.id,
    );
  }
}
