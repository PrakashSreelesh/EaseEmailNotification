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
} from "lucide-react";

interface StatCard {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: "blue" | "teal" | "orange" | "red";
}

export default function Dashboard() {
  const { user } = useAuth();
  const isSuperAdmin = user?.role === "super_admin";

  // Mock data - in production, these would come from API calls
  const assetCards: StatCard[] = isSuperAdmin
    ? [
        {
          label: "Standard Users",
          value: "24",
          icon: <Users className="w-6 h-6" />,
          color: "blue",
        },
        {
          label: "Applications",
          value: "12",
          icon: <Package className="w-6 h-6" />,
          color: "teal",
        },
        {
          label: "SMTP Accounts",
          value: "8",
          icon: <Mail className="w-6 h-6" />,
          color: "orange",
        },
        {
          label: "Templates",
          value: "34",
          icon: <FileText className="w-6 h-6" />,
          color: "blue",
        },
      ]
    : [
        {
          label: "My Applications",
          value: "3",
          icon: <Package className="w-6 h-6" />,
          color: "teal",
        },
        {
          label: "SMTP Accounts",
          value: "2",
          icon: <Mail className="w-6 h-6" />,
          color: "orange",
        },
        {
          label: "Templates",
          value: "5",
          icon: <FileText className="w-6 h-6" />,
          color: "blue",
        },
        {
          label: "API Keys",
          value: "4",
          icon: <Package className="w-6 h-6" />,
          color: "blue",
        },
      ];

  const analyticsCards: StatCard[] = [
    {
      label: "Emails Sent",
      value: "15,234",
      icon: <TrendingUp className="w-6 h-6" />,
      color: "blue",
    },
    {
      label: "Delivered",
      value: "14,891",
      icon: <CheckCircle2 className="w-6 h-6" />,
      color: "teal",
    },
    {
      label: "Failed",
      value: "127",
      icon: <AlertCircle className="w-6 h-6" />,
      color: "red",
    },
    {
      label: "Pending",
      value: "216",
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
            <h3 className="text-lg font-semibold text-foreground mb-4">
              Recent Activity
            </h3>
            <div className="space-y-3">
              <div className="flex items-center gap-3 pb-3 border-b border-border">
                <Mail className="w-5 h-5 text-accent flex-shrink-0" />
                <div className="text-sm">
                  <p className="font-medium text-foreground">
                    500 emails sent
                  </p>
                  <p className="text-xs text-muted-foreground">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-center gap-3 pb-3 border-b border-border">
                <FileText className="w-5 h-5 text-secondary flex-shrink-0" />
                <div className="text-sm">
                  <p className="font-medium text-foreground">
                    Template created
                  </p>
                  <p className="text-xs text-muted-foreground">5 hours ago</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Package className="w-5 h-5 text-primary flex-shrink-0" />
                <div className="text-sm">
                  <p className="font-medium text-foreground">App registered</p>
                  <p className="text-xs text-muted-foreground">1 day ago</p>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6 border-border">
            <h3 className="text-lg font-semibold text-foreground mb-4">
              Quick Stats
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-foreground font-medium">
                    Delivery Rate
                  </span>
                  <span className="text-sm font-semibold text-secondary">
                    97.5%
                  </span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-secondary rounded-full transition-all duration-300"
                    style={{ width: "97.5%" }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-foreground font-medium">
                    Bounce Rate
                  </span>
                  <span className="text-sm font-semibold text-accent">
                    1.2%
                  </span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent rounded-full transition-all duration-300"
                    style={{ width: "1.2%" }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-foreground font-medium">
                    Open Rate
                  </span>
                  <span className="text-sm font-semibold text-primary">
                    42.3%
                  </span>
                </div>
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-300"
                    style={{ width: "42.3%" }}
                  ></div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
