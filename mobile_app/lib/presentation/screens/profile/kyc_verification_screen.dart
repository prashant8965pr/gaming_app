import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/utils/validators.dart';
import '../../widgets/custom_button.dart' as custom;

/// KYC Verification screen for document upload
class KYCVerificationScreen extends StatefulWidget {
  const KYCVerificationScreen({super.key});

  @override
  State<KYCVerificationScreen> createState() => _KYCVerificationScreenState();
}

class _KYCVerificationScreenState extends State<KYCVerificationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _panController = TextEditingController();
  final _aadhaarController = TextEditingController();
  final _addressController = TextEditingController();

  File? _panCardImage;
  File? _aadhaarFrontImage;
  File? _aadhaarBackImage;
  File? _addressProofImage;

  String _kycStatus = 'not_submitted'; // not_submitted, pending, verified, rejected
  String? _rejectionReason;

  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadKYCStatus();
  }

  @override
  void dispose() {
    _panController.dispose();
    _aadhaarController.dispose();
    _addressController.dispose();
    super.dispose();
  }

  void _loadKYCStatus() {
    // TODO: Load KYC status from BLoC
    // Mock data for demonstration
    setState(() {
      _kycStatus = 'not_submitted'; // or 'pending', 'verified', 'rejected'
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('KYC Verification'),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_kycStatus == 'verified') {
      return _buildVerifiedStatus();
    } else if (_kycStatus == 'pending') {
      return _buildPendingStatus();
    } else if (_kycStatus == 'rejected') {
      return _buildRejectedStatus();
    } else {
      return _buildKYCForm();
    }
  }

  Widget _buildVerifiedStatus() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: AppColors.success.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.verified_user,
                size: 64,
                color: AppColors.success,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'KYC Verified',
              style: AppTextStyles.heading1.copyWith(
                color: AppColors.success,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Your account has been successfully verified',
              style: AppTextStyles.body.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  _buildVerifiedDetail('PAN Card', 'ABCDE1234F'),
                  const Divider(height: 24),
                  _buildVerifiedDetail('Aadhaar', '****-****-5678'),
                  const Divider(height: 24),
                  _buildVerifiedDetail('Verified On', '15 Nov 2024'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVerifiedDetail(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: AppTextStyles.body.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        Text(
          value,
          style: AppTextStyles.bodyBold,
        ),
      ],
    );
  }

  Widget _buildPendingStatus() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                color: AppColors.warning.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.pending,
                size: 64,
                color: AppColors.warning,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Verification Pending',
              style: AppTextStyles.heading1.copyWith(
                color: AppColors.warning,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Your KYC documents are under review. We will notify you once the verification is complete.',
              style: AppTextStyles.body.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.info.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppColors.info.withOpacity(0.3),
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.access_time,
                    color: AppColors.info,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Verification usually takes 24-48 hours',
                      style: AppTextStyles.body.copyWith(
                        color: AppColors.info,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRejectedStatus() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: AppColors.danger.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.cancel,
              size: 64,
              color: AppColors.danger,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Verification Rejected',
            style: AppTextStyles.heading1.copyWith(
              color: AppColors.danger,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'Your KYC verification was rejected. Please review the reason and resubmit.',
            style: AppTextStyles.body.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.danger.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: AppColors.danger.withOpacity(0.3),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.error_outline,
                      color: AppColors.danger,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'Rejection Reason',
                      style: AppTextStyles.bodyBold.copyWith(
                        color: AppColors.danger,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  _rejectionReason ?? 'Document image is unclear. Please upload a clear photo.',
                  style: AppTextStyles.body.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
          custom.CustomButton(
            text: 'Resubmit KYC',
            onPressed: () {
              setState(() {
                _kycStatus = 'not_submitted';
              });
            },
            icon: Icons.refresh,
            buttonStyle: custom.ButtonStyle.primary,
          ),
        ],
      ),
    );
  }

  Widget _buildKYCForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Info Card
            _buildInfoCard(),

            const SizedBox(height: 24),

            // PAN Card Section
            Text(
              'PAN Card Details',
              style: AppTextStyles.heading3,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _panController,
              decoration: const InputDecoration(
                labelText: 'PAN Number',
                hintText: 'Enter PAN number',
                prefixIcon: Icon(Icons.credit_card),
              ),
              textCapitalization: TextCapitalization.characters,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter PAN number';
                }
                final panRegex = RegExp(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$');
                if (!panRegex.hasMatch(value)) {
                  return 'Invalid PAN format';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            _buildDocumentUpload(
              'Upload PAN Card',
              'Clear photo of your PAN card',
              _panCardImage,
              () => _pickDocument('pan'),
            ),

            const SizedBox(height: 24),

            // Aadhaar Card Section
            Text(
              'Aadhaar Card Details',
              style: AppTextStyles.heading3,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _aadhaarController,
              decoration: const InputDecoration(
                labelText: 'Aadhaar Number',
                hintText: 'Enter Aadhaar number',
                prefixIcon: Icon(Icons.badge),
              ),
              keyboardType: TextInputType.number,
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Please enter Aadhaar number';
                }
                if (value.replaceAll(' ', '').length != 12) {
                  return 'Aadhaar must be 12 digits';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            _buildDocumentUpload(
              'Upload Aadhaar Front',
              'Front side of your Aadhaar card',
              _aadhaarFrontImage,
              () => _pickDocument('aadhaar_front'),
            ),
            const SizedBox(height: 12),
            _buildDocumentUpload(
              'Upload Aadhaar Back',
              'Back side of your Aadhaar card',
              _aadhaarBackImage,
              () => _pickDocument('aadhaar_back'),
            ),

            const SizedBox(height: 24),

            // Address Proof Section
            Text(
              'Address Proof (Optional)',
              style: AppTextStyles.heading3,
            ),
            const SizedBox(height: 12),
            _buildDocumentUpload(
              'Upload Address Proof',
              'Utility bill, bank statement, etc.',
              _addressProofImage,
              () => _pickDocument('address'),
            ),

            const SizedBox(height: 32),

            // Terms & Conditions
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.warning.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppColors.warning.withOpacity(0.3),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.security,
                        color: AppColors.warning,
                        size: 20,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Important Information',
                        style: AppTextStyles.bodyBold.copyWith(
                          color: AppColors.warning,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '• All documents must be clear and readable\n'
                    '• Name on documents should match your profile\n'
                    '• Documents will be verified within 24-48 hours\n'
                    '• Your data is encrypted and secure',
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Submit Button
            custom.CustomButton(
              text: 'Submit for Verification',
              onPressed: _handleSubmit,
              icon: Icons.send,
              buttonStyle: custom.ButtonStyle.primary,
              isLoading: _isLoading,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.verified_user,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Why KYC?',
                  style: AppTextStyles.bodyBold.copyWith(
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'KYC verification is required for withdrawals and compliance with gaming regulations.',
                  style: AppTextStyles.caption.copyWith(
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDocumentUpload(
    String title,
    String subtitle,
    File? image,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: image != null
                ? AppColors.success.withOpacity(0.5)
                : Colors.grey.shade300,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: image != null
                    ? AppColors.success.withOpacity(0.1)
                    : AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: image != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.file(
                        image,
                        fit: BoxFit.cover,
                      ),
                    )
                  : Icon(
                      Icons.upload_file,
                      color: image != null
                          ? AppColors.success
                          : AppColors.primary,
                      size: 32,
                    ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTextStyles.bodyBold,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    image != null ? 'Document uploaded ✓' : subtitle,
                    style: AppTextStyles.caption.copyWith(
                      color: image != null
                          ? AppColors.success
                          : AppColors.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              image != null ? Icons.check_circle : Icons.arrow_forward_ios,
              color:
                  image != null ? AppColors.success : AppColors.textSecondary,
              size: 20,
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _pickDocument(String type) async {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Upload Document',
              style: AppTextStyles.heading3,
            ),
            const SizedBox(height: 20),
            ListTile(
              leading: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.camera_alt,
                  color: AppColors.primary,
                ),
              ),
              title: const Text('Take Photo'),
              subtitle: const Text('Use camera to capture document'),
              onTap: () {
                Navigator.pop(context);
                _selectImage(ImageSource.camera, type);
              },
            ),
            ListTile(
              leading: Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.success.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.photo_library,
                  color: AppColors.success,
                ),
              ),
              title: const Text('Choose from Gallery'),
              subtitle: const Text('Select existing photo'),
              onTap: () {
                Navigator.pop(context);
                _selectImage(ImageSource.gallery, type);
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _selectImage(ImageSource source, String type) async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? image = await picker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1920,
        imageQuality: 85,
      );

      if (image != null) {
        setState(() {
          switch (type) {
            case 'pan':
              _panCardImage = File(image.path);
              break;
            case 'aadhaar_front':
              _aadhaarFrontImage = File(image.path);
              break;
            case 'aadhaar_back':
              _aadhaarBackImage = File(image.path);
              break;
            case 'address':
              _addressProofImage = File(image.path);
              break;
          }
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to pick image: $e'),
          backgroundColor: AppColors.danger,
        ),
      );
    }
  }

  void _handleSubmit() {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_panCardImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please upload PAN card image'),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }

    if (_aadhaarFrontImage == null || _aadhaarBackImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please upload both sides of Aadhaar card'),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    // TODO: Submit KYC documents via BLoC
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _kycStatus = 'pending';
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('KYC documents submitted successfully'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    });
  }
}
