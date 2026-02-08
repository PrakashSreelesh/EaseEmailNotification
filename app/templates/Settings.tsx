import { useState } from "react";
import Layout from "@/components/Layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/context/AuthContext";
import {
  Save,
  Bell,
  Shield,
  Eye,
  EyeOff,
  Mail,
  User,
  Lock,
  Smartphone,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { toast } from "sonner";

interface UserSettings {
  email: string;
  fullName: string;
  companyName: string;
  timezone: string;
  language: string;
}

interface NotificationSettings {
  emailSentNotifications: boolean;
  failureAlerts: boolean;
  weeklyReports: boolean;
  securityAlerts: boolean;
}

export default function Settings() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<"account" | "notifications" | "security">(
    "account"
  );
  const [showPassword, setShowPassword] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const [userSettings, setUserSettings] = useState<UserSettings>({
    email: user?.email || "",
    fullName: user?.name || "",
    companyName: "My Company",
    timezone: "UTC",
    language: "English",
  });

  const [notificationSettings, setNotificationSettings] =
    useState<NotificationSettings>({
      emailSentNotifications: true,
      failureAlerts: true,
      weeklyReports: true,
      securityAlerts: true,
    });

  const handleSaveUserSettings = async () => {
    setIsSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 800));
    toast.success("Account settings saved successfully");
    setIsSaving(false);
  };

  const handleSaveNotifications = async () => {
    setIsSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 800));
    toast.success("Notification preferences updated");
    setIsSaving(false);
  };

  const tabs = [
    { id: "account" as const, label: "Account Settings", icon: <User /> },
    { id: "notifications" as const, label: "Notifications", icon: <Bell /> },
    { id: "security" as const, label: "Security", icon: <Shield /> },
  ];

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account settings and preferences
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-border">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
                activeTab === tab.id
                  ? "border-accent text-accent"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Account Settings Tab */}
        {activeTab === "account" && (
          <div className="space-y-6">
            <Card className="p-6 border-border space-y-6 animate-in fade-in duration-300">
              <div>
                <h2 className="text-xl font-semibold text-foreground mb-6">
                  Profile Information
                </h2>

                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium">Email Address</Label>
                    <Input
                      type="email"
                      value={userSettings.email}
                      onChange={(e) =>
                        setUserSettings({
                          ...userSettings,
                          email: e.target.value,
                        })
                      }
                      className="mt-1"
                      disabled
                    />
                    <p className="text-xs text-muted-foreground mt-2">
                      Your email cannot be changed. Contact support for email
                      changes.
                    </p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium">Full Name</Label>
                    <Input
                      value={userSettings.fullName}
                      onChange={(e) =>
                        setUserSettings({
                          ...userSettings,
                          fullName: e.target.value,
                        })
                      }
                      className="mt-1"
                      placeholder="John Doe"
                    />
                  </div>

                  <div>
                    <Label className="text-sm font-medium">Company Name</Label>
                    <Input
                      value={userSettings.companyName}
                      onChange={(e) =>
                        setUserSettings({
                          ...userSettings,
                          companyName: e.target.value,
                        })
                      }
                      className="mt-1"
                      placeholder="Your Company"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium">Timezone</Label>
                      <select
                        value={userSettings.timezone}
                        onChange={(e) =>
                          setUserSettings({
                            ...userSettings,
                            timezone: e.target.value,
                          })
                        }
                        className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
                      >
                        <option>UTC</option>
                        <option>EST (UTC-5)</option>
                        <option>CST (UTC-6)</option>
                        <option>MST (UTC-7)</option>
                        <option>PST (UTC-8)</option>
                        <option>IST (UTC+5:30)</option>
                      </select>
                    </div>

                    <div>
                      <Label className="text-sm font-medium">Language</Label>
                      <select
                        value={userSettings.language}
                        onChange={(e) =>
                          setUserSettings({
                            ...userSettings,
                            language: e.target.value,
                          })
                        }
                        className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
                      >
                        <option>English</option>
                        <option>Spanish</option>
                        <option>French</option>
                        <option>German</option>
                        <option>Chinese</option>
                      </select>
                    </div>
                  </div>
                </div>

                <Button
                  onClick={handleSaveUserSettings}
                  disabled={isSaving}
                  className="gap-2 btn-primary mt-6 h-10"
                >
                  <Save className="w-4 h-4" />
                  {isSaving ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === "notifications" && (
          <div className="space-y-6">
            <Card className="p-6 border-border space-y-6 animate-in fade-in duration-300">
              <h2 className="text-xl font-semibold text-foreground">
                Notification Preferences
              </h2>

              <div className="space-y-4">
                {[
                  {
                    key: "emailSentNotifications" as const,
                    title: "Email Sent Notifications",
                    description: "Get notified when emails are sent",
                  },
                  {
                    key: "failureAlerts" as const,
                    title: "Failure Alerts",
                    description: "Alert me when emails fail to send",
                  },
                  {
                    key: "weeklyReports" as const,
                    title: "Weekly Reports",
                    description: "Receive weekly email activity reports",
                  },
                  {
                    key: "securityAlerts" as const,
                    title: "Security Alerts",
                    description: "Alerts about suspicious account activity",
                  },
                ].map((notification) => (
                  <label
                    key={notification.key}
                    className="flex items-center p-4 rounded-lg border border-border hover:bg-muted/30 transition-colors cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={
                        notificationSettings[notification.key]
                      }
                      onChange={(e) =>
                        setNotificationSettings({
                          ...notificationSettings,
                          [notification.key]: e.target.checked,
                        })
                      }
                      className="w-4 h-4 rounded accent-accent cursor-pointer"
                    />
                    <div className="ml-4 flex-1">
                      <p className="font-medium text-foreground">
                        {notification.title}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {notification.description}
                      </p>
                    </div>
                    {notificationSettings[notification.key] ? (
                      <CheckCircle2 className="w-5 h-5 text-green-600" />
                    ) : null}
                  </label>
                ))}
              </div>

              <Button
                onClick={handleSaveNotifications}
                disabled={isSaving}
                className="gap-2 btn-primary h-10"
              >
                <Save className="w-4 h-4" />
                {isSaving ? "Saving..." : "Save Preferences"}
              </Button>
            </Card>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === "security" && (
          <div className="space-y-6">
            {/* Change Password */}
            <Card className="p-6 border-border space-y-6 animate-in fade-in duration-300">
              <h2 className="text-xl font-semibold text-foreground">
                Change Password
              </h2>

              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">Current Password</Label>
                  <div className="relative mt-1">
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-medium">New Password</Label>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium">
                    Confirm New Password
                  </Label>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    className="mt-1"
                  />
                </div>

                <Button className="gap-2 btn-primary h-10">
                  <Lock className="w-4 h-4" />
                  Update Password
                </Button>
              </div>
            </Card>

            {/* Active Sessions */}
            <Card className="p-6 border-border space-y-6">
              <h2 className="text-xl font-semibold text-foreground">
                Active Sessions
              </h2>

              <div className="space-y-3">
                <div className="flex items-center p-4 rounded-lg border border-border bg-gradient-to-r from-background to-muted/20">
                  <div className="flex-1">
                    <p className="font-medium text-foreground flex items-center gap-2">
                      <Smartphone className="w-4 h-4" />
                      This Browser
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Current session
                    </p>
                  </div>
                  <span className="text-xs font-semibold px-3 py-1 rounded-full bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300">
                    Active
                  </span>
                </div>
              </div>

              <Button
                variant="outline"
                className="w-full text-destructive hover:bg-destructive/10"
              >
                Sign Out All Other Sessions
              </Button>
            </Card>

            {/* Danger Zone */}
            <Card className="p-6 border-destructive bg-red-50/50 dark:bg-red-950/20 border-red-200 dark:border-red-800 space-y-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-foreground mb-2">
                    Danger Zone
                  </h3>
                  <p className="text-sm text-foreground/80">
                    Irreversible and destructive actions
                  </p>
                </div>
              </div>

              <Button
                onClick={() => {
                  if (
                    confirm(
                      "Are you sure you want to delete your account? This cannot be undone."
                    )
                  ) {
                    logout();
                    toast.success("Account deleted");
                  }
                }}
                variant="outline"
                className="w-full text-destructive hover:bg-destructive/10 border-destructive"
              >
                Delete Account
              </Button>
            </Card>
          </div>
        )}
      </div>
    </Layout>
  );
}
