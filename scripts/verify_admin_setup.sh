#!/bin/bash

# Admin Panel Setup Verification Script
# This script checks if the admin panel environment is properly configured

echo "========================================="
echo "Admin Panel Setup Verification"
echo "========================================="
echo ""

# Check 1: Backend directory
echo "✓ Checking backend directory..."
if [ -d "backend" ]; then
    echo "  ✅ Backend directory exists"
else
    echo "  ❌ Backend directory not found"
    exit 1
fi

# Check 2: Frontend admin directory
echo "✓ Checking frontend-admin directory..."
if [ -d "frontend-admin" ]; then
    echo "  ✅ Frontend-admin directory exists"
else
    echo "  ❌ Frontend-admin directory not found"
    exit 1
fi

# Check 3: Frontend admin .env.local
echo "✓ Checking frontend-admin/.env.local..."
if [ -f "frontend-admin/.env.local" ]; then
    echo "  ✅ .env.local file exists"
    cat frontend-admin/.env.local
else
    echo "  ❌ .env.local file not found"
    echo "  Creating .env.local file..."
    cat > frontend-admin/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=Gaming Platform Admin
NEXT_PUBLIC_APP_VERSION=1.0.0
EOF
    echo "  ✅ .env.local file created"
fi

# Check 4: Node modules
echo "✓ Checking node_modules..."
if [ -d "frontend-admin/node_modules" ]; then
    echo "  ✅ node_modules exists"
else
    echo "  ⚠️  node_modules not found"
    echo "  Run: cd frontend-admin && npm install"
fi

# Check 5: Package.json
echo "✓ Checking package.json..."
if [ -f "frontend-admin/package.json" ]; then
    echo "  ✅ package.json exists"
else
    echo "  ❌ package.json not found"
    exit 1
fi

# Check 6: Database migration
echo "✓ Checking if role migration exists..."
if [ -f "backend/alembic/versions/004_phase_8_admin_role.py" ]; then
    echo "  ✅ Role migration file exists"
else
    echo "  ❌ Role migration file not found"
fi

echo ""
echo "========================================="
echo "Setup Status Summary"
echo "========================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Start Backend:"
echo "   cd backend"
echo "   # Activate your virtual environment"
echo "   # Run: uvicorn main:app --reload"
echo ""
echo "2. Apply Migration (if not done):"
echo "   cd backend"
echo "   alembic upgrade head"
echo ""
echo "3. Create Admin User:"
echo "   # Connect to your database and run:"
echo "   # UPDATE users SET role = 'admin' WHERE username = 'your_username';"
echo ""
echo "4. Install Frontend Dependencies (if not done):"
echo "   cd frontend-admin"
echo "   npm install"
echo ""
echo "5. Start Frontend Admin:"
echo "   cd frontend-admin"
echo "   npm run dev"
echo ""
echo "6. Access Admin Panel:"
echo "   http://localhost:3001"
echo ""
echo "========================================="
echo "✅ Setup verification complete!"
echo "========================================="
