/**
 * Landing Page
 */

import Link from 'next/link';
import { Trophy, Gamepad2, Wallet, Award } from 'lucide-react';
import { Button } from '@/components/common';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Play. Compete. Win!
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              India's premier skill-based gaming platform. Test your skills and win real cash prizes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/register">
                <Button size="lg" variant="secondary">
                  Get Started
                </Button>
              </Link>
              <Link href="/games">
                <Button size="lg" variant="outline" className="bg-white/10 border-white text-white hover:bg-white/20">
                  Browse Games
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900 dark:text-white">
            Why Choose Us?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <FeatureCard
              icon={<Gamepad2 className="w-12 h-12" />}
              title="Skill-Based Games"
              description="Play fair games where skill matters, not luck"
            />
            <FeatureCard
              icon={<Wallet className="w-12 h-12" />}
              title="Secure Payments"
              description="Fast and secure deposits and withdrawals"
            />
            <FeatureCard
              icon={<Award className="w-12 h-12" />}
              title="Daily Rewards"
              description="Earn bonuses, achievements, and referral rewards"
            />
            <FeatureCard
              icon={<Trophy className="w-12 h-12" />}
              title="Leaderboards"
              description="Compete globally and climb the ranks"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-950">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
            Ready to Start Winning?
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
            Join thousands of players already earning on our platform
          </p>
          <Link href="/auth/register">
            <Button size="lg">
              Create Free Account
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center p-6">
      <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 rounded-full mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
        {title}
      </h3>
      <p className="text-gray-600 dark:text-gray-400">
        {description}
      </p>
    </div>
  );
}
