import 'package:equatable/equatable.dart';

class TournamentModel extends Equatable {
  final String id;
  final String name;
  final String? description;
  final String gameId;
  final String gameName;
  final String tournamentType;
  final int entryFee;
  final int prizePool;
  final Map<String, dynamic> prizeDistribution;
  final int maxParticipants;
  final int currentParticipants;
  final DateTime startTime;
  final DateTime registrationStart;
  final DateTime registrationEnd;
  final String status;
  final Map<String, dynamic>? bracketData;
  final Map<String, dynamic>? rules;
  final bool isFeatured;
  final bool isPublic;
  final DateTime createdAt;

  const TournamentModel({
    required this.id,
    required this.name,
    this.description,
    required this.gameId,
    required this.gameName,
    required this.tournamentType,
    required this.entryFee,
    required this.prizePool,
    required this.prizeDistribution,
    required this.maxParticipants,
    required this.currentParticipants,
    required this.startTime,
    required this.registrationStart,
    required this.registrationEnd,
    required this.status,
    this.bracketData,
    this.rules,
    required this.isFeatured,
    required this.isPublic,
    required this.createdAt,
  });

  factory TournamentModel.fromJson(Map<String, dynamic> json) {
    return TournamentModel(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      gameId: json['game_id'],
      gameName: json['game_name'] ?? '',
      tournamentType: json['tournament_type'],
      entryFee: json['entry_fee'],
      prizePool: json['prize_pool'],
      prizeDistribution: json['prize_distribution'] ?? {},
      maxParticipants: json['max_participants'],
      currentParticipants: json['current_participants'],
      startTime: DateTime.parse(json['start_time']),
      registrationStart: DateTime.parse(json['registration_start']),
      registrationEnd: DateTime.parse(json['registration_end']),
      status: json['status'],
      bracketData: json['bracket_data'],
      rules: json['rules'],
      isFeatured: json['is_featured'] ?? false,
      isPublic: json['is_public'] ?? true,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'game_id': gameId,
      'game_name': gameName,
      'tournament_type': tournamentType,
      'entry_fee': entryFee,
      'prize_pool': prizePool,
      'prize_distribution': prizeDistribution,
      'max_participants': maxParticipants,
      'current_participants': currentParticipants,
      'start_time': startTime.toIso8601String(),
      'registration_start': registrationStart.toIso8601String(),
      'registration_end': registrationEnd.toIso8601String(),
      'status': status,
      'bracket_data': bracketData,
      'rules': rules,
      'is_featured': isFeatured,
      'is_public': isPublic,
      'created_at': createdAt.toIso8601String(),
    };
  }

  bool get isRegistrationOpen {
    final now = DateTime.now();
    return now.isAfter(registrationStart) &&
        now.isBefore(registrationEnd) &&
        currentParticipants < maxParticipants &&
        status == 'upcoming';
  }

  bool get isFull => currentParticipants >= maxParticipants;

  String get statusDisplay {
    switch (status) {
      case 'upcoming':
        return 'Upcoming';
      case 'registration_open':
        return 'Registration Open';
      case 'registration_closed':
        return 'Registration Closed';
      case 'in_progress':
        return 'Live';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  String get tournamentTypeDisplay {
    switch (tournamentType) {
      case 'single_elimination':
        return 'Single Elimination';
      case 'double_elimination':
        return 'Double Elimination';
      case 'round_robin':
        return 'Round Robin';
      default:
        return tournamentType;
    }
  }

  @override
  List<Object?> get props => [
        id,
        name,
        description,
        gameId,
        gameName,
        tournamentType,
        entryFee,
        prizePool,
        prizeDistribution,
        maxParticipants,
        currentParticipants,
        startTime,
        registrationStart,
        registrationEnd,
        status,
        bracketData,
        rules,
        isFeatured,
        isPublic,
        createdAt,
      ];
}

class TournamentRegistrationModel extends Equatable {
  final String id;
  final String tournamentId;
  final String userId;
  final int? seedNumber;
  final String status;
  final String paymentStatus;
  final int? finalRank;
  final int prizeWon;
  final DateTime registeredAt;
  final TournamentModel? tournament;

  const TournamentRegistrationModel({
    required this.id,
    required this.tournamentId,
    required this.userId,
    this.seedNumber,
    required this.status,
    required this.paymentStatus,
    this.finalRank,
    required this.prizeWon,
    required this.registeredAt,
    this.tournament,
  });

  factory TournamentRegistrationModel.fromJson(Map<String, dynamic> json) {
    return TournamentRegistrationModel(
      id: json['id'],
      tournamentId: json['tournament_id'],
      userId: json['user_id'],
      seedNumber: json['seed_number'],
      status: json['status'],
      paymentStatus: json['payment_status'],
      finalRank: json['final_rank'],
      prizeWon: json['prize_won'] ?? 0,
      registeredAt: DateTime.parse(json['registered_at']),
      tournament: json['tournament'] != null
          ? TournamentModel.fromJson(json['tournament'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tournament_id': tournamentId,
      'user_id': userId,
      'seed_number': seedNumber,
      'status': status,
      'payment_status': paymentStatus,
      'final_rank': finalRank,
      'prize_won': prizeWon,
      'registered_at': registeredAt.toIso8601String(),
      'tournament': tournament?.toJson(),
    };
  }

  @override
  List<Object?> get props => [
        id,
        tournamentId,
        userId,
        seedNumber,
        status,
        paymentStatus,
        finalRank,
        prizeWon,
        registeredAt,
        tournament,
      ];
}

class TournamentMatchModel extends Equatable {
  final String id;
  final String tournamentId;
  final int roundNumber;
  final int matchNumber;
  final String? player1Id;
  final String? player2Id;
  final String? player1Name;
  final String? player2Name;
  final String? winnerId;
  final Map<String, dynamic>? scoreData;
  final String status;
  final bool isFinals;
  final DateTime? scheduledAt;
  final DateTime? completedAt;

  const TournamentMatchModel({
    required this.id,
    required this.tournamentId,
    required this.roundNumber,
    required this.matchNumber,
    this.player1Id,
    this.player2Id,
    this.player1Name,
    this.player2Name,
    this.winnerId,
    this.scoreData,
    required this.status,
    required this.isFinals,
    this.scheduledAt,
    this.completedAt,
  });

  factory TournamentMatchModel.fromJson(Map<String, dynamic> json) {
    return TournamentMatchModel(
      id: json['id'],
      tournamentId: json['tournament_id'],
      roundNumber: json['round_number'],
      matchNumber: json['match_number'],
      player1Id: json['player1_id'],
      player2Id: json['player2_id'],
      player1Name: json['player1_name'],
      player2Name: json['player2_name'],
      winnerId: json['winner_id'],
      scoreData: json['score_data'],
      status: json['status'],
      isFinals: json['is_finals'] ?? false,
      scheduledAt: json['scheduled_at'] != null
          ? DateTime.parse(json['scheduled_at'])
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tournament_id': tournamentId,
      'round_number': roundNumber,
      'match_number': matchNumber,
      'player1_id': player1Id,
      'player2_id': player2Id,
      'player1_name': player1Name,
      'player2_name': player2Name,
      'winner_id': winnerId,
      'score_data': scoreData,
      'status': status,
      'is_finals': isFinals,
      'scheduled_at': scheduledAt?.toIso8601String(),
      'completed_at': completedAt?.toIso8601String(),
    };
  }

  @override
  List<Object?> get props => [
        id,
        tournamentId,
        roundNumber,
        matchNumber,
        player1Id,
        player2Id,
        player1Name,
        player2Name,
        winnerId,
        scoreData,
        status,
        isFinals,
        scheduledAt,
        completedAt,
      ];
}

class TournamentBracketModel extends Equatable {
  final String type;
  final int numRounds;
  final List<BracketRoundModel> rounds;

  const TournamentBracketModel({
    required this.type,
    required this.numRounds,
    required this.rounds,
  });

  factory TournamentBracketModel.fromJson(Map<String, dynamic> json) {
    return TournamentBracketModel(
      type: json['type'],
      numRounds: json['num_rounds'],
      rounds: (json['rounds'] as List)
          .map((round) => BracketRoundModel.fromJson(round))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'num_rounds': numRounds,
      'rounds': rounds.map((round) => round.toJson()).toList(),
    };
  }

  @override
  List<Object?> get props => [type, numRounds, rounds];
}

class BracketRoundModel extends Equatable {
  final int roundNumber;
  final List<TournamentMatchModel> matches;

  const BracketRoundModel({
    required this.roundNumber,
    required this.matches,
  });

  factory BracketRoundModel.fromJson(Map<String, dynamic> json) {
    return BracketRoundModel(
      roundNumber: json['round_number'],
      matches: (json['matches'] as List)
          .map((match) => TournamentMatchModel.fromJson(match))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'round_number': roundNumber,
      'matches': matches.map((match) => match.toJson()).toList(),
    };
  }

  @override
  List<Object?> get props => [roundNumber, matches];
}
