import Layout from "@/components/Layout";
import { useAuth } from "@/context/AuthContext";
import { Card } from "@/components/ui/card";
import {
  Users,
  Package,
  Mail,
  FileText,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Clock,
  RefreshCw,
} from "lucide-react";
import { useState, useEffect } from "react";

interface StatCard {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: "blue" | "teal" | "orange" | "red";
}

interface EmailStats {
  sent: number;
  delivered: number;
  failed: number;
  pending: number;
}

interface QuickStats {
  delivery_rate: number;
  bounce_rate: number;
  open_rate: number;
}

interface RecentActivity {
  icon: string;
  title: string;
  subtitle: string;
  time: string;
}

interface DashboardData {
  usersCount: number;
  applicationsCount: number;
  smtpCount: number;
  templatesCount: number;
  emailStats: EmailStats;
  recentActivity: RecentActivity[];
  quickStats: QuickStats;
}

interface LoadingState {
  users: boolean;
  applications: boolean;
  smtp: boolean;
  templates: boolean;
  emailStats: boolean;
  recentActivity: boolean;
  quickStats: boolean;
}

interface ErrorState {
  users: string | null;
  applications: string | null;
  smtp: string | null;
  templates: string | null;
  emailStats: string | null;
  recentActivity: string | null;
  quickStats: string | null;
}

export default function Dashboard() {
  const { user } = useAuth();
  const isSuperAdmin = user?.role === "super_admin";

  // State management
  const [data, setData] = useState<DashboardData>({
    usersCount: 0,
    applicationsCount: 0,
    smtpCount: 0,
    templatesCount: 0,
    emailStats: { sent: 0, delivered: 0, failed: 0, pending: 0 },
    recentActivity: [],
    quickStats: { delivery_rate: 0, bounce_rate: 0, open_rate: 0 }
  });

  const [loading, setLoading] = useState<LoadingState>({
    users: true,
    applications: true,
    smtp: true,
    templates: true,
    emailStats: true,
    recentActivity: true,
    quickStats: true
  });

  const [errors, setErrors] = useState<ErrorState>({
    users: null,
    applications: null,
    smtp: null,
    templates: null,
    emailStats: null,
    recentActivity: null,
    quickStats: null
  });

  // API fetch functions
  const fetchData = async (endpoint: string, key: keyof DashboardData) => {
    try {
      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          // Redirect to login on auth errors
          window.location.href = '/login';
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (key === 'usersCount' || key === 'applicationsCount' || key === 'smtpCount' || key === 'templatesCount') {
        setData(prev => ({ ...prev, [key]: result.count || 0 }));
      } else {
        setData(prev => ({ ...prev, [key]: result }));
      }

      setErrors(prev => ({ ...prev, [key]: null }));
    } catch (error) {
      console.error(`Error fetching ${key}:`, error);
      setErrors(prev => ({ ...prev, [key]: error instanceof Error ? error.message : 'Unknown error' }));
    } finally {
      const loadingKey = key as keyof LoadingState;
      setLoading(prev => ({ ...prev, [loadingKey]: false }));
    }
  };

  // Fetch all data on component mount
  useEffect(() => {
    const fetchAllData = async () => {
      const tenantId = user?.tenant_id || '';
      const isSuperAdminParam = isSuperAdmin ? 'true' : 'false';

      // Fetch counts
      await Promise.all([
        fetchData(`/api/v1/users?count_only=true&is_superadmin=${isSuperAdminParam}&tenant_id=${tenantId}`, 'usersCount'),
        fetchData(`/api/v1/applications?count_only=true&is_superadmin=${isSuperAdminParam}&tenant_id=${tenantId}`, 'applicationsCount'),
        fetchData(`/api/v1/smtp-accounts?count_only=true&is_superadmin=${isSuperAdminParam}&tenant_id=${tenantId}`, 'smtpCount'),
        fetchData(`/api/v1/templates?count_only=true&is_superadmin=${isSuperAdminParam}&tenant_id=${tenantId}`, 'templatesCount'),
        fetchData('/api/v1/email-stats', 'emailStats'),
        fetchData('/api/v1/recent-activity', 'recentActivity'),
        fetchData('/api/v1/quick-stats', 'quickStats')
      ]);
    };

    fetchAllData();
  }, [user, isSuperAdmin]);

  // Create dynamic stat cards
  const assetCards: StatCard[] = isSuperAdmin
    ? [
        {
          label: "Standard Users",
          value: loading.users ? "..." : data.usersCount.toString(),
          icon: <Users className="w-6 h-6" />,
          color: "blue",
        },
        {
          label: "Applications",
          value: loading.applications ? "..." : data.applicationsCount.toString(),
          icon: <Package className="w-6 h-6" />,
          color: "teal",
        },
        {
          label: "SMTP Accounts",
          value: loading.smtp ? "..." : data.smtpCount.toString(),
          icon: <Mail className="w-6 h-6" />,
          color: "orange",
        },
        {
          label: "Templates",
          value: loading.templates ? "..." : data.templatesCount.toString(),
          icon: <FileText className="w-6 h-6" />,
          color: "blue",
        },
      ]
    : [
        {
          label: "My Applications",
          value: loading.applications ? "..." : data.applicationsCount.toString(),
          icon: <Package className="w-6 h-6" />,
          color: "teal",
        },
        {
          label: "SMTP Accounts",
          value: loading.smtp ? "..." : data.smtpCount.toString(),
          icon: <Mail className="w-6 h-6" />,
          color: "orange",
        },
        {
          label: "Templates",
          value: loading.templates ? "..." : data.templatesCount.toString(),
          icon: <FileText className="w-6 h-6" />,
          color: "blue",
        },
        {
          label: "API Keys",
          value: "4", // This would need its own endpoint
          icon: <Package className="w-6 h-6" />,
          color: "blue",
        },
      ];

  const analyticsCards: StatCard[] = [
    {
      label: "Emails Sent",
      value: loading.emailStats ? "..." : data.emailStats.sent.toLocaleString(),
      icon: <TrendingUp className="w-6 h-6" />,
      color: "blue",
    },
    {
      label: "Delivered",
      value: loading.emailStats ? "..." : data.emailStats.delivered.toLocaleString(),
      icon: <CheckCircle2 className="w-6 h-6" />,
      color: "teal",
    },
    {
      label: "Failed",
      value: loading.emailStats ? "..." : data.emailStats.failed.toString(),
      icon: <AlertCircle className="w-6 h-6" />,
      color: "red",
    },
    {
      label: "Pending",
      value: loading.emailStats ? "..." : data.emailStats.pending.toString(),
      icon: <Clock className="w-6 h-6" />,
      color: "orange",
    },
  ];

  const getColorClasses = (color: string) => {
    const colorMap: Record<
      string,
      { bg: string; text: string; border: string }
    > = {
      blue: {
        bg: "bg-blue-50 dark:bg-blue-950",
        text: "text-primary",
        border: "border-blue-200 dark:border-blue-800",
      },
      teal: {
        bg: "bg-cyan-50 dark:bg-cyan-950",
        text: "text-secondary",
        border: "border-cyan-200 dark:border-cyan-800",
      },
      orange: {
        bg: "bg-orange-50 dark:bg-orange-950",
        text: "text-accent",
        border: "border-orange-200 dark:border-orange-800",
      },
      red: {
        bg: "bg-red-50 dark:bg-red-950",
        text: "text-destructive",
        border: "border-red-200 dark:border-red-800",
      },
    };
    return colorMap[color] || colorMap["blue"];
  };

  const StatCardComponent = ({ card }: { card: StatCard }) => {
    const colors = getColorClasses(card.color);
    return (
      <Card className={`p-6 border ${colors.border} ${colors.bg}`}>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{card.label}</p>
            <p className={`text-3xl font-bold ${colors.text} mt-2`}>
              {card.value}
            </p>
          </div>
          <div className={colors.text}>{card.icon}</div>
        </div>
      </Card>
    );
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Welcome back,{" "}
            <span className="font-semibold text-foreground">
              {user?.email.split("@")[0]}
            </span>
            ! Here's an overview of your email operations.
          </p>
        </div>

        {/* Assets Section */}
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-4">
            {isSuperAdmin ? "System Overview" : "Your Resources"}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {assetCards.map((card, idx) => (
              <StatCardComponent key={idx} card={card} />
            ))}
          </div>
        </div>

        {/* Analytics Section */}
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-4">
            Email Analytics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {analyticsCards.map((card, idx) => (
              <StatCardComponent key={idx} card={card} />
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6 border-border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground">
                Recent Activity
              </h3>
              <button
                onClick={() => {
                  setLoading(prev => ({ ...prev, recentActivity: true }));
                  setErrors(prev => ({ ...prev, recentActivity: null }));
                  fetchData('/api/v1/recent-activity', 'recentActivity');
                }}
                className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
                disabled={loading.recentActivity}
              >
                <RefreshCw className={`w-4 h-4 ${loading.recentActivity ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
            {errors.recentActivity ? (
              <div className="text-sm text-destructive">
                Error loading recent activity: {errors.recentActivity}
              </div>
            ) : (
              <div className="space-y-3">
                {loading.recentActivity ? (
                  <div className="space-y-3">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="flex items-center gap-3 pb-3 border-b border-border">
                        <div className="w-5 h-5 bg-muted rounded animate-pulse" />
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-muted rounded animate-pulse w-3/4" />
                          <div className="h-3 bg-muted rounded animate-pulse w-1/2" />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : data.recentActivity.length > 0 ? (
                  data.recentActivity.map((activity, index) => {
                    const iconMap = {
                      'mail': <Mail className="w-5 h-5 text-accent flex-shrink-0" />,
                      'file-text': <FileText className="w-5 h-5 text-secondary flex-shrink-0" />,
                      'package': <Package className="w-5 h-5 text-primary flex-shrink-0" />,
                      'check-circle': <CheckCircle2 className="w-5 h-5 text-teal-500 flex-shrink-0" />,
                      'alert-circle': <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />,
                      'clock': <Clock className="w-5 h-5 text-orange-500 flex-shrink-0" />
                    };

                    return (
                      <div key={index} className={`flex items-center gap-3 ${index < data.recentActivity.length - 1 ? 'pb-3 border-b border-border' : ''}`}>
                        {iconMap[activity.icon as keyof typeof iconMap] || <Mail className="w-5 h-5 text-accent flex-shrink-0" />}
                        <div className="text-sm">
                          <p className="font-medium text-foreground">
                            {activity.title}
                          </p>
                          <p className="text-xs text-muted-foreground">{activity.subtitle}</p>
                          <p className="text-xs text-muted-foreground">{activity.time}</p>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="text-sm text-muted-foreground">
                    No recent activity to display.
                  </div>
                )}
              </div>
            )}
          </Card>

          <Card className="p-6 border-border">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-foreground">
                Quick Stats
              </h3>
              <button
                onClick={() => {
                  setLoading(prev => ({ ...prev, quickStats: true }));
                  setErrors(prev => ({ ...prev, quickStats: null }));
                  fetchData('/api/v1/quick-stats', 'quickStats');
                }}
                className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
                disabled={loading.quickStats}
              >
                <RefreshCw className={`w-4 h-4 ${loading.quickStats ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
            {errors.quickStats ? (
              <div className="text-sm text-destructive">
                Error loading quick stats: {errors.quickStats}
              </div>
            ) : (
              <div className="space-y-4">
                {loading.quickStats ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="space-y-2">
                        <div className="flex justify-between">
                          <div className="h-4 bg-muted rounded animate-pulse w-24" />
                          <div className="h-4 bg-muted rounded animate-pulse w-12" />
                        </div>
                        <div className="w-full h-2 bg-muted rounded-full animate-pulse" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-foreground font-medium">
                          Delivery Rate
                        </span>
                        <span className="text-sm font-semibold text-secondary">
                          {data.quickStats.delivery_rate}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-secondary rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(data.quickStats.delivery_rate, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-foreground font-medium">
                          Bounce Rate
                        </span>
                        <span className="text-sm font-semibold text-accent">
                          {data.quickStats.bounce_rate}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-accent rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(data.quickStats.bounce_rate, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm text-foreground font-medium">
                          Open Rate
                        </span>
                        <span className="text-sm font-semibold text-primary">
                          {data.quickStats.open_rate}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full transition-all duration-300"
                          style={{ width: `${Math.min(data.quickStats.open_rate, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </Card>
        </div>
      </div>
    </Layout>
  );
}
