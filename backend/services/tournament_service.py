"""
Tournament service with bracket generation and management
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math
import random

from models.tournament import Tournament, TournamentRegistration, TournamentMatch
from models.user import User
from models.wallet import Wallet, WalletTransaction


class TournamentService:
    """Service for tournament management"""
    
    @staticmethod
    def create_tournament(db: Session, tournament_data: dict, creator_id: str) -> Tournament:
        """Create a new tournament"""
        tournament = Tournament(
            name=tournament_data['name'],
            description=tournament_data.get('description'),
            game_id=tournament_data['game_id'],
            tournament_type=tournament_data.get('tournament_type', 'single_elimination'),
            entry_fee=tournament_data['entry_fee'],
            prize_pool=tournament_data.get('prize_pool', 0),
            prize_distribution=tournament_data.get('prize_distribution', {"1st": 50, "2nd": 30, "3rd": 20}),
            max_participants=tournament_data.get('max_participants', 16),
            min_participants=tournament_data.get('min_participants', 4),
            start_time=tournament_data['start_time'],
            registration_start=tournament_data['registration_start'],
            registration_end=tournament_data['registration_end'],
            rules=tournament_data.get('rules'),
            is_featured=tournament_data.get('is_featured', False),
            is_public=tournament_data.get('is_public', True),
            created_by=creator_id
        )
        
        db.add(tournament)
        db.commit()
        db.refresh(tournament)
        return tournament
    
    @staticmethod
    def register_for_tournament(db: Session, tournament_id: str, user_id: str) -> TournamentRegistration:
        """Register user for tournament"""
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        
        if not tournament:
            raise ValueError("Tournament not found")
        
        if tournament.current_participants >= tournament.max_participants:
            raise ValueError("Tournament is full")
        
        if datetime.utcnow() > tournament.registration_end:
            raise ValueError("Registration period has ended")
        
        # Check if already registered
        existing = db.query(TournamentRegistration).filter(
            and_(
                TournamentRegistration.tournament_id == tournament_id,
                TournamentRegistration.user_id == user_id
            )
        ).first()
        
        if existing:
            raise ValueError("Already registered for this tournament")
        
        # Deduct entry fee from wallet
        wallet = db.query(Wallet).filter(
            and_(
                Wallet.user_id == user_id,
                Wallet.wallet_type == 'cash'
            )
        ).first()
        
        if not wallet or wallet.balance < tournament.entry_fee:
            raise ValueError("Insufficient balance")
        
        # Create registration
        registration = TournamentRegistration(
            tournament_id=tournament_id,
            user_id=user_id,
            status='registered',
            payment_status='completed'
        )
        
        # Deduct entry fee
        wallet.balance -= tournament.entry_fee
        
        # Create wallet transaction
        transaction = WalletTransaction(
            user_id=user_id,
            wallet_id=wallet.id,
            amount=tournament.entry_fee,
            transaction_type='debit',
            category='tournament_entry',
            description=f"Entry fee for tournament: {tournament.name}",
            status='completed'
        )
        
        # Update tournament participant count
        tournament.current_participants += 1
        tournament.prize_pool += tournament.entry_fee
        
        db.add(registration)
        db.add(transaction)
        db.commit()
        db.refresh(registration)
        
        return registration
    
    @staticmethod
    def generate_bracket(db: Session, tournament_id: str) -> Dict:
        """Generate tournament bracket"""
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        
        if not tournament:
            raise ValueError("Tournament not found")
        
        # Get all registered participants
        registrations = db.query(TournamentRegistration).filter(
            and_(
                TournamentRegistration.tournament_id == tournament_id,
                TournamentRegistration.status == 'registered'
            )
        ).all()
        
        if len(registrations) < tournament.min_participants:
            raise ValueError(f"Not enough participants. Minimum: {tournament.min_participants}")
        
        # Shuffle and assign seed numbers
        random.shuffle(registrations)
        for idx, reg in enumerate(registrations):
            reg.seed_number = idx + 1
        
        if tournament.tournament_type == 'single_elimination':
            return TournamentService._generate_single_elimination_bracket(
                db, tournament, registrations
            )
        elif tournament.tournament_type == 'double_elimination':
            return TournamentService._generate_double_elimination_bracket(
                db, tournament, registrations
            )
        else:
            raise ValueError(f"Unsupported tournament type: {tournament.tournament_type}")
    
    @staticmethod
    def _generate_single_elimination_bracket(
        db: Session,
        tournament: Tournament,
        registrations: List[TournamentRegistration]
    ) -> Dict:
        """Generate single elimination bracket"""
        num_participants = len(registrations)
        
        # Calculate number of rounds needed
        num_rounds = math.ceil(math.log2(num_participants))
        total_spots = 2 ** num_rounds
        
        # Create bracket structure
        bracket = {
            'type': 'single_elimination',
            'num_rounds': num_rounds,
            'rounds': []
        }
        
        # Round 1 matches
        round_1_matches = []
        match_number = 1
        
        participants_list = [reg.user_id for reg in registrations]
        
        # Add byes if needed
        num_byes = total_spots - num_participants
        for _ in range(num_byes):
            participants_list.append(None)  # Bye
        
        # Create first round matches
        for i in range(0, len(participants_list), 2):
            player1_id = participants_list[i]
            player2_id = participants_list[i + 1] if i + 1 < len(participants_list) else None
            
            match = TournamentMatch(
                tournament_id=tournament.id,
                round_number=1,
                match_number=match_number,
                player1_id=player1_id,
                player2_id=player2_id,
                status='pending' if player1_id and player2_id else 'walkover',
                winner_id=player1_id if not player2_id else None  # Auto-advance if bye
            )
            
            db.add(match)
            round_1_matches.append(match.to_dict())
            match_number += 1
        
        bracket['rounds'].append({'round_number': 1, 'matches': round_1_matches})
        
        # Create subsequent rounds (empty for now, filled as matches complete)
        for round_num in range(2, num_rounds + 1):
            num_matches = 2 ** (num_rounds - round_num)
            round_matches = []
            
            for i in range(num_matches):
                match = TournamentMatch(
                    tournament_id=tournament.id,
                    round_number=round_num,
                    match_number=i + 1,
                    status='pending',
                    is_finals=(round_num == num_rounds)
                )
                db.add(match)
                round_matches.append(match.to_dict())
            
            bracket['rounds'].append({'round_number': round_num, 'matches': round_matches})
        
        # Save bracket to tournament
        tournament.bracket_data = bracket
        tournament.status = 'registration_closed'
        
        db.commit()
        return bracket
    
    @staticmethod
    def _generate_double_elimination_bracket(
        db: Session,
        tournament: Tournament,
        registrations: List[TournamentRegistration]
    ) -> Dict:
        """Generate double elimination bracket (simplified)"""
        # For now, similar to single elimination but with losers bracket
        # Full implementation would create two parallel brackets
        return TournamentService._generate_single_elimination_bracket(db, tournament, registrations)
    
    @staticmethod
    def submit_match_result(
        db: Session,
        match_id: str,
        winner_id: str,
        score_data: Dict
    ) -> TournamentMatch:
        """Submit result for a match"""
        match = db.query(TournamentMatch).filter(TournamentMatch.id == match_id).first()
        
        if not match:
            raise ValueError("Match not found")
        
        if match.status == 'completed':
            raise ValueError("Match already completed")
        
        if winner_id not in [str(match.player1_id), str(match.player2_id)]:
            raise ValueError("Winner must be one of the players")
        
        # Update match
        match.winner_id = winner_id
        match.score_data = score_data
        match.status = 'completed'
        match.completed_at = datetime.utcnow()
        
        # Advance winner to next round
        TournamentService._advance_winner(db, match)
        
        # Check if tournament is complete
        TournamentService._check_tournament_completion(db, match.tournament_id)
        
        db.commit()
        db.refresh(match)
        return match
    
    @staticmethod
    def _advance_winner(db: Session, completed_match: TournamentMatch):
        """Advance winner to next round"""
        tournament = completed_match.tournament
        current_round = completed_match.round_number
        current_match_num = completed_match.match_number
        
        # Find next round match
        next_round = current_round + 1
        next_match_num = (current_match_num + 1) // 2
        
        next_match = db.query(TournamentMatch).filter(
            and_(
                TournamentMatch.tournament_id == tournament.id,
                TournamentMatch.round_number == next_round,
                TournamentMatch.match_number == next_match_num
            )
        ).first()
        
        if next_match:
            # Assign winner to next match
            if current_match_num % 2 == 1:  # Odd match number -> player1 of next match
                next_match.player1_id = completed_match.winner_id
            else:  # Even match number -> player2 of next match
                next_match.player2_id = completed_match.winner_id
            
            # If both players are assigned, match is ready
            if next_match.player1_id and next_match.player2_id:
                next_match.status = 'ready'
    
    @staticmethod
    def _check_tournament_completion(db: Session, tournament_id: str):
        """Check if tournament is complete and distribute prizes"""
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        
        # Check if finals match is complete
        finals_match = db.query(TournamentMatch).filter(
            and_(
                TournamentMatch.tournament_id == tournament_id,
                TournamentMatch.is_finals == True,
                TournamentMatch.status == 'completed'
            )
        ).first()
        
        if finals_match:
            # Tournament complete - distribute prizes
            TournamentService._distribute_prizes(db, tournament, finals_match)
            tournament.status = 'completed'
            tournament.end_time = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def _distribute_prizes(db: Session, tournament: Tournament, finals_match: TournamentMatch):
        """Distribute prizes to winners"""
        prize_pool = tournament.prize_pool
        distribution = tournament.prize_distribution or {"1st": 50, "2nd": 30, "3rd": 20}
        
        # 1st place (finals winner)
        first_place_prize = int(prize_pool * distribution.get("1st", 50) / 100)
        TournamentService._award_prize(db, finals_match.winner_id, first_place_prize, tournament.id, 1)
        
        # 2nd place (finals loser)
        second_place_id = finals_match.player1_id if finals_match.winner_id == finals_match.player2_id else finals_match.player2_id
        second_place_prize = int(prize_pool * distribution.get("2nd", 30) / 100)
        TournamentService._award_prize(db, second_place_id, second_place_prize, tournament.id, 2)
        
        # 3rd place (semi-final losers - simplified)
        if "3rd" in distribution:
            third_place_prize = int(prize_pool * distribution["3rd"] / 100)
            # Find semi-final losers and split prize
            # Simplified: just note in tournament completion
    
    @staticmethod
    def _award_prize(db: Session, user_id: str, amount: int, tournament_id: str, rank: int):
        """Award prize to user"""
        # Update wallet
        wallet = db.query(Wallet).filter(
            and_(
                Wallet.user_id == user_id,
                Wallet.wallet_type == 'winnings'
            )
        ).first()
        
        if wallet:
            wallet.balance += amount
            
            # Create transaction
            transaction = WalletTransaction(
                user_id=user_id,
                wallet_id=wallet.id,
                amount=amount,
                transaction_type='credit',
                category='tournament_prize',
                description=f"Tournament prize - Rank {rank}",
                status='completed'
            )
            db.add(transaction)
            
            # Update registration
            registration = db.query(TournamentRegistration).filter(
                and_(
                    TournamentRegistration.tournament_id == tournament_id,
                    TournamentRegistration.user_id == user_id
                )
            ).first()
            
            if registration:
                registration.final_rank = rank
                registration.prize_won = amount
                registration.status = 'winner' if rank == 1 else 'eliminated'
