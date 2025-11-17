import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';
import '../../bloc/tournament/tournament_bloc.dart';
import '../../bloc/tournament/tournament_event.dart';
import '../../bloc/tournament/tournament_state.dart';
import '../../../data/models/tournament_model.dart';

class TournamentDetailsScreen extends StatefulWidget {
  final String tournamentId;

  const TournamentDetailsScreen({
    Key? key,
    required this.tournamentId,
  }) : super(key: key);

  @override
  State<TournamentDetailsScreen> createState() =>
      _TournamentDetailsScreenState();
}

class _TournamentDetailsScreenState extends State<TournamentDetailsScreen> {
  @override
  void initState() {
    super.initState();
    _loadTournamentDetails();
  }

  void _loadTournamentDetails() {
    context
        .read<TournamentBloc>()
        .add(LoadTournamentDetails(widget.tournamentId));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Tournament Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              // TODO: Implement share functionality
            },
          ),
        ],
      ),
      body: BlocConsumer<TournamentBloc, TournamentState>(
        listener: (context, state) {
          if (state is TournamentError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(state.message)),
            );
          } else if (state is TournamentRegistered) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Successfully registered for tournament!'),
                backgroundColor: Colors.green,
              ),
            );
            _loadTournamentDetails();
          }
        },
        builder: (context, state) {
          if (state is TournamentDetailsLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state is TournamentDetailsLoaded) {
            return _buildContent(state.tournament);
          }

          return const Center(child: Text('Failed to load tournament'));
        },
      ),
    );
  }

  Widget _buildContent(TournamentModel tournament) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(tournament),
          const Divider(height: 1),
          _buildInfoSection(tournament),
          const Divider(height: 1),
          _buildPrizePoolSection(tournament),
          const Divider(height: 1),
          _buildRulesSection(tournament),
          const Divider(height: 1),
          _buildParticipantsSection(tournament),
          const SizedBox(height: 80), // Space for FAB
        ],
      ),
    );
  }

  Widget _buildHeader(TournamentModel tournament) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Theme.of(context).primaryColor, Colors.purple],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  tournament.name,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
              if (tournament.isFeatured)
                const Icon(Icons.star, color: Colors.amber, size: 32),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            tournament.gameName,
            style: const TextStyle(
              fontSize: 16,
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildHeaderChip(
                icon: Icons.people,
                label:
                    '${tournament.currentParticipants}/${tournament.maxParticipants}',
              ),
              const SizedBox(width: 12),
              _buildHeaderChip(
                icon: Icons.emoji_events,
                label: '₹${tournament.prizePool}',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHeaderChip({required IconData icon, required String label}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: Colors.white),
          const SizedBox(width: 6),
          Text(
            label,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoSection(TournamentModel tournament) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Tournament Info',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildInfoRow('Type', tournament.tournamentTypeDisplay),
          _buildInfoRow('Entry Fee', '₹${tournament.entryFee}'),
          _buildInfoRow('Start Time',
              DateFormat('MMM dd, yyyy - HH:mm').format(tournament.startTime)),
          _buildInfoRow(
              'Registration Closes',
              DateFormat('MMM dd, yyyy - HH:mm')
                  .format(tournament.registrationEnd)),
          _buildInfoRow('Status', tournament.statusDisplay),
          if (tournament.description != null) ...[
            const SizedBox(height: 16),
            Text(
              tournament.description!,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[700],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPrizePoolSection(TournamentModel tournament) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.emoji_events, color: Colors.amber),
              const SizedBox(width: 8),
              const Text(
                'Prize Pool',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildPrizeCard(
            rank: '1st Place',
            amount: (tournament.prizePool *
                    (tournament.prizeDistribution['1st'] ?? 50) /
                    100)
                .toInt(),
            color: Colors.amber,
          ),
          _buildPrizeCard(
            rank: '2nd Place',
            amount: (tournament.prizePool *
                    (tournament.prizeDistribution['2nd'] ?? 30) /
                    100)
                .toInt(),
            color: Colors.grey,
          ),
          _buildPrizeCard(
            rank: '3rd Place',
            amount: (tournament.prizePool *
                    (tournament.prizeDistribution['3rd'] ?? 20) /
                    100)
                .toInt(),
            color: Colors.orange,
          ),
        ],
      ),
    );
  }

  Widget _buildPrizeCard({
    required String rank,
    required int amount,
    required Color color,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(Icons.emoji_events, color: color, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              rank,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
          Text(
            '₹$amount',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRulesSection(TournamentModel tournament) {
    if (tournament.rules == null || tournament.rules!.isEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Rules & Regulations',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          // Display rules from tournament.rules map
          ...tournament.rules!.entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.check_circle, size: 20, color: Colors.green),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      '${entry.key}: ${entry.value}',
                      style: const TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildParticipantsSection(TournamentModel tournament) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Participants',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: LinearProgressIndicator(
                  value:
                      tournament.currentParticipants / tournament.maxParticipants,
                  backgroundColor: Colors.grey[200],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    tournament.isFull ? Colors.red : Colors.green,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '${tournament.currentParticipants}/${tournament.maxParticipants}',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          if (tournament.isFull) ...[
            const SizedBox(height: 8),
            Text(
              'Tournament is full!',
              style: TextStyle(
                color: Colors.red[700],
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget? _buildFloatingActionButton(TournamentModel tournament) {
    if (!tournament.isRegistrationOpen) {
      return null;
    }

    return FloatingActionButton.extended(
      onPressed: () => _showRegistrationDialog(tournament),
      icon: const Icon(Icons.login),
      label: Text('Register (₹${tournament.entryFee})'),
    );
  }

  void _showRegistrationDialog(TournamentModel tournament) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Register for Tournament'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Tournament: ${tournament.name}'),
            const SizedBox(height: 8),
            Text('Entry Fee: ₹${tournament.entryFee}'),
            const SizedBox(height: 16),
            const Text(
              'Are you sure you want to register? The entry fee will be deducted from your wallet.',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context
                  .read<TournamentBloc>()
                  .add(RegisterForTournament(tournament.id));
            },
            child: const Text('Confirm'),
          ),
        ],
      ),
    );
  }
}
