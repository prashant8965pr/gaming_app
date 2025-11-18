import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../data/models/kyc_model.dart';
import '../../../data/repositories/kyc_repository.dart';

// Events
abstract class KycEvent extends Equatable {
  const KycEvent();
  @override
  List<Object?> get props => [];
}

class LoadKycStatus extends KycEvent {}

class SubmitKyc extends KycEvent {
  final String documentType;
  final String documentNumber;
  final String frontImagePath;
  final String backImagePath;
  final String selfiePath;

  const SubmitKyc({
    required this.documentType,
    required this.documentNumber,
    required this.frontImagePath,
    required this.backImagePath,
    required this.selfiePath,
  });

  @override
  List<Object?> get props => [
        documentType,
        documentNumber,
        frontImagePath,
        backImagePath,
        selfiePath,
      ];
}

class ResubmitKyc extends KycEvent {
  final int kycId;
  final String frontImagePath;
  final String backImagePath;
  final String selfiePath;

  const ResubmitKyc({
    required this.kycId,
    required this.frontImagePath,
    required this.backImagePath,
    required this.selfiePath,
  });

  @override
  List<Object?> get props => [kycId, frontImagePath, backImagePath, selfiePath];
}

// State
enum KycStatus { initial, loading, loaded, submitting, error }

class KycState extends Equatable {
  final KycStatus status;
  final KycModel? kycData;
  final String? errorMessage;
  final bool isVerified;
  final bool isPending;
  final bool needsResubmission;

  const KycState({
    this.status = KycStatus.initial,
    this.kycData,
    this.errorMessage,
    this.isVerified = false,
    this.isPending = false,
    this.needsResubmission = false,
  });

  KycState copyWith({
    KycStatus? status,
    KycModel? kycData,
    String? errorMessage,
    bool? isVerified,
    bool? isPending,
    bool? needsResubmission,
  }) {
    return KycState(
      status: status ?? this.status,
      kycData: kycData ?? this.kycData,
      errorMessage: errorMessage,
      isVerified: isVerified ?? this.isVerified,
      isPending: isPending ?? this.isPending,
      needsResubmission: needsResubmission ?? this.needsResubmission,
    );
  }

  @override
  List<Object?> get props => [
        status,
        kycData,
        errorMessage,
        isVerified,
        isPending,
        needsResubmission,
      ];
}

// BLoC
class KycBloc extends Bloc<KycEvent, KycState> {
  final KycRepository kycRepository;

  KycBloc({required this.kycRepository}) : super(const KycState()) {
    on<LoadKycStatus>(_onLoadKycStatus);
    on<SubmitKyc>(_onSubmitKyc);
    on<ResubmitKyc>(_onResubmitKyc);
  }

  Future<void> _onLoadKycStatus(LoadKycStatus event, Emitter<KycState> emit) async {
    emit(state.copyWith(status: KycStatus.loading));
    final result = await kycRepository.getKycStatus();
    result.fold(
      (failure) => emit(state.copyWith(
        status: KycStatus.loaded,
        isVerified: false,
        isPending: false,
      )),
      (kycData) {
        final isVerified = kycData.status == 'approved';
        final isPending = kycData.status == 'pending';
        final needsResubmission = kycData.status == 'resubmit_requested';

        emit(state.copyWith(
          status: KycStatus.loaded,
          kycData: kycData,
          isVerified: isVerified,
          isPending: isPending,
          needsResubmission: needsResubmission,
        ));
      },
    );
  }

  Future<void> _onSubmitKyc(SubmitKyc event, Emitter<KycState> emit) async {
    emit(state.copyWith(status: KycStatus.submitting));

    final result = await kycRepository.submitKyc(
      documentType: event.documentType,
      documentNumber: event.documentNumber,
      frontImagePath: event.frontImagePath,
      backImagePath: event.backImagePath,
      selfiePath: event.selfiePath,
    );

    result.fold(
      (failure) => emit(state.copyWith(
        status: KycStatus.error,
        errorMessage: failure.message,
      )),
      (kycData) => emit(state.copyWith(
        status: KycStatus.loaded,
        kycData: kycData,
        isPending: true,
      )),
    );
  }

  Future<void> _onResubmitKyc(ResubmitKyc event, Emitter<KycState> emit) async {
    emit(state.copyWith(status: KycStatus.submitting));

    final result = await kycRepository.resubmitKyc(
      kycId: event.kycId,
      frontImagePath: event.frontImagePath,
      backImagePath: event.backImagePath,
      selfiePath: event.selfiePath,
    );

    result.fold(
      (failure) => emit(state.copyWith(
        status: KycStatus.error,
        errorMessage: failure.message,
      )),
      (kycData) => emit(state.copyWith(
        status: KycStatus.loaded,
        kycData: kycData,
        isPending: true,
        needsResubmission: false,
      )),
    );
  }
}
