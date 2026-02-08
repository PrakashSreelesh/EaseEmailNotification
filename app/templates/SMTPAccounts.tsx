import { useState } from "react";
import Layout from "@/components/Layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Plus,
  Edit2,
  Trash2,
  Eye,
  EyeOff,
  Save,
  X,
  Search,
  Mail,
  CheckCircle2,
  AlertCircle,
  Server,
} from "lucide-react";
import { toast } from "sonner";

interface SMTPAccount {
  id: string;
  name: string;
  provider: string;
  host: string;
  port: number;
  username: string;
  password: string;
  fromEmail: string;
  status: "active" | "inactive";
  createdAt: string;
  connectedApps: number;
}

const mockAccounts: SMTPAccount[] = [
  {
    id: "1",
    name: "Primary SMTP",
    provider: "Gmail",
    host: "smtp.gmail.com",
    port: 587,
    username: "noreply@example.com",
    password: "••••••••••••",
    fromEmail: "noreply@example.com",
    status: "active",
    createdAt: "2024-01-15",
    connectedApps: 3,
  },
  {
    id: "2",
    name: "SendGrid",
    provider: "SendGrid",
    host: "smtp.sendgrid.net",
    port: 587,
    username: "apikey",
    password: "••••••••••••",
    fromEmail: "support@example.com",
    status: "active",
    createdAt: "2024-01-10",
    connectedApps: 5,
  },
];

export default function SMTPAccounts() {
  const [accounts, setAccounts] = useState<SMTPAccount[]>(mockAccounts);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedAccount, setSelectedAccount] = useState<SMTPAccount | null>(
    null
  );
  const [isEditing, setIsEditing] = useState(false);
  const [showPassword, setShowPassword] = useState<string | null>(null);
  const [editData, setEditData] = useState<Partial<SMTPAccount>>({});

  const filteredAccounts = accounts.filter(
    (a) =>
      a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.provider.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleNewAccount = () => {
    setEditData({
      name: "",
      provider: "Gmail",
      host: "",
      port: 587,
      username: "",
      password: "",
      fromEmail: "",
      status: "inactive",
    });
    setSelectedAccount(null);
    setIsEditing(true);
  };

  const handleEdit = (account: SMTPAccount) => {
    setSelectedAccount(account);
    setEditData(account);
    setIsEditing(true);
    setShowPassword(null);
  };

  const handleSave = () => {
    if (!editData.name || !editData.host || !editData.port || !editData.username) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (selectedAccount) {
      setAccounts(
        accounts.map((a) =>
          a.id === selectedAccount.id
            ? {
                ...selectedAccount,
                ...editData,
              }
            : a
        )
      );
      toast.success("SMTP account updated successfully");
    } else {
      const newAccount: SMTPAccount = {
        id: `smtp_${Date.now()}`,
        name: editData.name || "",
        provider: editData.provider || "Gmail",
        host: editData.host || "",
        port: editData.port || 587,
        username: editData.username || "",
        password: editData.password || "",
        fromEmail: editData.fromEmail || "",
        status: editData.status || "inactive",
        createdAt: new Date().toISOString().split("T")[0],
        connectedApps: 0,
      };
      setAccounts([...accounts, newAccount]);
      toast.success("SMTP account created successfully");
    }

    setIsEditing(false);
    setSelectedAccount(null);
    setEditData({});
  };

  const handleDelete = (id: string) => {
    setAccounts(accounts.filter((a) => a.id !== id));
    toast.success("SMTP account deleted");
  };

  const toggleStatus = (account: SMTPAccount) => {
    const updated = accounts.map((a) =>
      a.id === account.id
        ? { ...a, status: a.status === "active" ? "inactive" : "active" }
        : a
    );
    setAccounts(updated);
    toast.success(
      `SMTP account ${account.status === "active" ? "deactivated" : "activated"}`
    );
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              SMTP Accounts
            </h1>
            <p className="text-muted-foreground mt-2">
              Configure and manage your SMTP email providers
            </p>
          </div>
          <Button
            onClick={handleNewAccount}
            className="gap-2 btn-primary h-10"
          >
            <Plus className="w-4 h-4" />
            Add SMTP Account
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search by name or provider..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {!isEditing ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAccounts.length > 0 ? (
              filteredAccounts.map((account) => (
                <div
                  key={account.id}
                  className="group cursor-pointer"
                  onClick={() => handleEdit(account)}
                >
                  <Card className="p-6 border-border hover:border-accent transition-all duration-300 hover:shadow-lg hover:scale-[1.01] bg-gradient-to-r from-card to-card/50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Mail className="w-5 h-5 text-primary" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-foreground text-lg">
                              {account.name}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              {account.provider}
                            </p>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-xs text-muted-foreground font-medium">
                              HOST
                            </p>
                            <p className="text-sm text-foreground font-mono truncate">
                              {account.host}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground font-medium">
                              PORT
                            </p>
                            <p className="text-sm text-foreground font-mono">
                              {account.port}
                            </p>
                          </div>
                          <div className="col-span-2">
                            <p className="text-xs text-muted-foreground font-medium">
                              FROM EMAIL
                            </p>
                            <p className="text-sm text-foreground truncate">
                              {account.fromEmail}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col gap-3 ml-4">
                        <div
                          className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 dark:bg-green-950 cursor-pointer transition-all hover:scale-105"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleStatus(account);
                          }}
                        >
                          <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400" />
                          <span
                            className={`text-xs font-medium ${
                              account.status === "active"
                                ? "text-green-700 dark:text-green-300"
                                : "text-green-600 dark:text-green-400"
                            }`}
                          >
                            {account.status === "active" ? "Active" : "Inactive"}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-6 pt-6 border-t border-border">
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(account);
                        }}
                        variant="outline"
                        size="sm"
                        className="flex-1 gap-1"
                      >
                        <Edit2 className="w-3 h-3" />
                        Edit
                      </Button>
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(account.id);
                        }}
                        variant="outline"
                        size="sm"
                        className="text-destructive hover:bg-destructive/10"
                      >
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </Card>
                </div>
              ))
            ) : (
              <div className="col-span-full text-center py-12">
                <Server className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-30" />
                <p className="text-muted-foreground">No SMTP accounts found</p>
              </div>
            )}
          </div>
        ) : (
          /* Editor Panel */
          <Card className="border-border p-6 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-foreground">
                {selectedAccount ? "Edit SMTP Account" : "Create SMTP Account"}
              </h2>
              <button
                onClick={() => {
                  setIsEditing(false);
                  setSelectedAccount(null);
                  setEditData({});
                  setShowPassword(null);
                }}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Account Info */}
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">Account Name *</Label>
                  <Input
                    placeholder="e.g., Primary SMTP"
                    value={editData.name || ""}
                    onChange={(e) =>
                      setEditData({ ...editData, name: e.target.value })
                    }
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium">Provider</Label>
                  <select
                    value={editData.provider || "Gmail"}
                    onChange={(e) =>
                      setEditData({ ...editData, provider: e.target.value })
                    }
                    className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
                  >
                    <option>Gmail</option>
                    <option>SendGrid</option>
                    <option>AWS SES</option>
                    <option>Mailgun</option>
                    <option>Custom</option>
                  </select>
                </div>

                <div>
                  <Label className="text-sm font-medium">From Email *</Label>
                  <Input
                    type="email"
                    placeholder="noreply@example.com"
                    value={editData.fromEmail || ""}
                    onChange={(e) =>
                      setEditData({ ...editData, fromEmail: e.target.value })
                    }
                    className="mt-1"
                  />
                </div>
              </div>

              {/* Connection Details */}
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">SMTP Host *</Label>
                  <Input
                    placeholder="smtp.gmail.com"
                    value={editData.host || ""}
                    onChange={(e) =>
                      setEditData({ ...editData, host: e.target.value })
                    }
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium">Port *</Label>
                  <Input
                    type="number"
                    placeholder="587"
                    value={editData.port || ""}
                    onChange={(e) =>
                      setEditData({
                        ...editData,
                        port: parseInt(e.target.value),
                      })
                    }
                    className="mt-1"
                  />
                </div>
              </div>

              {/* Authentication */}
              <div className="lg:col-span-2 space-y-4">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium">Username *</Label>
                    <Input
                      placeholder="your-email@example.com"
                      value={editData.username || ""}
                      onChange={(e) =>
                        setEditData({ ...editData, username: e.target.value })
                      }
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label className="text-sm font-medium">Password *</Label>
                    <div className="relative mt-1">
                      <Input
                        type={showPassword === "password" ? "text" : "password"}
                        placeholder="••••••••"
                        value={editData.password || ""}
                        onChange={(e) =>
                          setEditData({
                            ...editData,
                            password: e.target.value,
                          })
                        }
                      />
                      <button
                        type="button"
                        onClick={() =>
                          setShowPassword(
                            showPassword === "password" ? null : "password"
                          )
                        }
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword === "password" ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-3 pt-6 border-t border-border">
              <Button
                onClick={handleSave}
                className="gap-2 btn-primary flex-1 h-10"
              >
                <Save className="w-4 h-4" />
                {selectedAccount ? "Update" : "Create"} Account
              </Button>
              <Button
                onClick={() => {
                  setIsEditing(false);
                  setSelectedAccount(null);
                  setEditData({});
                  setShowPassword(null);
                }}
                variant="outline"
                className="flex-1 h-10"
              >
                Cancel
              </Button>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  );
}
