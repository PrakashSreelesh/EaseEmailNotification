import { useState } from "react";
import Layout from "@/components/Layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Plus,
  Trash2,
  Copy,
  Save,
  X,
  Search,
  Key,
  Calendar,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";
import { toast } from "sonner";

interface APIKey {
  id: string;
  name: string;
  key: string;
  environment: "development" | "production";
  status: "active" | "revoked";
  permissions: string[];
  createdAt: string;
  lastUsedAt?: string;
}

const mockAPIKeys: APIKey[] = [
  {
    id: "1",
    name: "Production API Key",
    key: "sk_live_abc123def456ghi789",
    environment: "production",
    status: "active",
    permissions: ["send:emails", "read:logs", "read:templates"],
    createdAt: "2024-01-10",
    lastUsedAt: "2024-01-20 14:30:00",
  },
  {
    id: "2",
    name: "Development API Key",
    key: "sk_test_xyz789uvw012qrs345",
    environment: "development",
    status: "active",
    permissions: ["send:emails", "read:logs", "read:templates", "write:templates"],
    createdAt: "2024-01-12",
    lastUsedAt: "2024-01-20 10:15:00",
  },
  {
    id: "3",
    name: "Old API Key",
    key: "sk_live_old_key_12345",
    environment: "production",
    status: "revoked",
    permissions: ["send:emails"],
    createdAt: "2023-12-01",
  },
];

export default function APIKeys() {
  const [apiKeys, setAPIKeys] = useState<APIKey[]>(mockAPIKeys);
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [showKey, setShowKey] = useState<string | null>(null);
  const [newKeyData, setNewKeyData] = useState({
    name: "",
    environment: "development" as const,
  });

  const filteredKeys = apiKeys.filter(
    (k) =>
      k.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.key.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreateKey = () => {
    if (!newKeyData.name) {
      toast.error("Please enter a key name");
      return;
    }

    const newKey: APIKey = {
      id: `key_${Date.now()}`,
      name: newKeyData.name,
      key: `sk_${newKeyData.environment === "production" ? "live" : "test"}_${Math.random().toString(36).substr(2, 20)}`,
      environment: newKeyData.environment,
      status: "active",
      permissions: ["send:emails", "read:logs", "read:templates"],
      createdAt: new Date().toISOString().split("T")[0],
      lastUsedAt: undefined,
    };

    setAPIKeys([...apiKeys, newKey]);
    toast.success("API key created successfully");
    setIsCreating(false);
    setNewKeyData({ name: "", environment: "development" });
    setShowKey(newKey.id);
  };

  const handleRevokeKey = (id: string) => {
    setAPIKeys(
      apiKeys.map((k) =>
        k.id === id ? { ...k, status: "revoked" as const } : k
      )
    );
    toast.success("API key revoked");
  };

  const handleDeleteKey = (id: string) => {
    setAPIKeys(apiKeys.filter((k) => k.id !== id));
    toast.success("API key deleted");
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">API Keys</h1>
            <p className="text-muted-foreground mt-2">
              Create and manage API keys for your applications
            </p>
          </div>
          <Button
            onClick={() => setIsCreating(!isCreating)}
            className="gap-2 btn-primary h-10"
          >
            <Plus className="w-4 h-4" />
            Create API Key
          </Button>
        </div>

        {/* Create Key Panel */}
        {isCreating && (
          <Card className="border-border p-6 space-y-4 animate-in fade-in slide-in-from-top-4 duration-300 bg-gradient-to-br from-accent/10 to-accent/5">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold text-foreground">
                Create New API Key
              </h3>
              <button
                onClick={() => setIsCreating(false)}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium">Key Name *</Label>
                <Input
                  placeholder="e.g., Production API Key"
                  value={newKeyData.name}
                  onChange={(e) =>
                    setNewKeyData({ ...newKeyData, name: e.target.value })
                  }
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Environment</Label>
                <select
                  value={newKeyData.environment}
                  onChange={(e) =>
                    setNewKeyData({
                      ...newKeyData,
                      environment: e.target.value as "development" | "production",
                    })
                  }
                  className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
                >
                  <option value="development">Development</option>
                  <option value="production">Production</option>
                </select>
              </div>
            </div>

            <p className="text-xs text-muted-foreground">
              Development keys are for testing. Production keys should be kept
              secure.
            </p>

            <div className="flex gap-3 pt-2">
              <Button
                onClick={handleCreateKey}
                className="gap-2 btn-primary flex-1 h-10"
              >
                <Save className="w-4 h-4" />
                Create Key
              </Button>
              <Button
                onClick={() => setIsCreating(false)}
                variant="outline"
                className="flex-1 h-10"
              >
                Cancel
              </Button>
            </div>
          </Card>
        )}

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search API keys by name or key..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* API Keys Grid */}
        <div className="space-y-4">
          {filteredKeys.length > 0 ? (
            filteredKeys.map((key) => (
              <div
                key={key.id}
                className="group"
              >
                <Card className={`p-6 border-border transition-all duration-300 hover:shadow-lg ${
                  key.status === "revoked"
                    ? "opacity-60 hover:opacity-100"
                    : "hover:-translate-y-1"
                } bg-gradient-to-r from-card to-card/50`}>
                  <div className="flex items-start justify-between mb-6">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Key className="w-5 h-5 text-accent" />
                        <h3 className="font-semibold text-foreground text-lg">
                          {key.name}
                        </h3>
                      </div>
                      <div className="flex items-center gap-3">
                        <span
                          className={`text-xs font-semibold px-3 py-1.5 rounded-full ${
                            key.environment === "production"
                              ? "bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300"
                              : "bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300"
                          }`}
                        >
                          {key.environment === "production"
                            ? "Production"
                            : "Development"}
                        </span>
                        <span
                          className={`text-xs font-semibold px-3 py-1.5 rounded-full flex items-center gap-1 ${
                            key.status === "active"
                              ? "bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300"
                              : "bg-gray-50 dark:bg-gray-950 text-gray-700 dark:text-gray-300"
                          }`}
                        >
                          {key.status === "active" ? (
                            <CheckCircle2 className="w-3 h-3" />
                          ) : (
                            <AlertCircle className="w-3 h-3" />
                          )}
                          {key.status === "active" ? "Active" : "Revoked"}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3 mb-6 p-4 bg-muted/30 rounded-lg">
                    <div>
                      <p className="text-xs text-muted-foreground font-medium mb-2">
                        API KEY
                      </p>
                      <div className="flex items-center gap-2">
                        <code className="text-xs bg-background border border-border rounded px-3 py-2 font-mono flex-1 truncate">
                          {showKey === key.id
                            ? key.key
                            : key.key.slice(0, 7) +
                              "•".repeat(Math.max(0, key.key.length - 14)) +
                              key.key.slice(-7)}
                        </code>
                        <button
                          onClick={() =>
                            setShowKey(showKey === key.id ? null : key.id)
                          }
                          className="text-muted-foreground hover:text-foreground transition-colors p-2 hover:bg-muted rounded"
                        >
                          {showKey === key.id ? (
                            <EyeOff className="w-4 h-4" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() => copyToClipboard(key.key)}
                          className="text-muted-foreground hover:text-foreground transition-colors p-2 hover:bg-muted rounded"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground font-medium mb-1">
                          CREATED
                        </p>
                        <p className="text-sm text-foreground flex items-center gap-2">
                          <Calendar className="w-3 h-3" />
                          {new Date(key.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                      {key.lastUsedAt && (
                        <div>
                          <p className="text-xs text-muted-foreground font-medium mb-1">
                            LAST USED
                          </p>
                          <p className="text-sm text-foreground">
                            {key.lastUsedAt}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="mb-4 p-3 bg-muted/20 rounded">
                    <p className="text-xs text-muted-foreground font-medium mb-2">
                      PERMISSIONS
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {key.permissions.map((perm) => (
                        <span
                          key={perm}
                          className="text-xs bg-primary/10 text-primary px-2 py-1 rounded"
                        >
                          {perm}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {key.status === "active" && (
                      <Button
                        onClick={() => handleRevokeKey(key.id)}
                        variant="outline"
                        size="sm"
                        className="flex-1 text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-950"
                      >
                        Revoke
                      </Button>
                    )}
                    <Button
                      onClick={() => handleDeleteKey(key.id)}
                      variant="outline"
                      size="sm"
                      className={
                        key.status === "active"
                          ? "text-destructive hover:bg-destructive/10"
                          : "flex-1 text-destructive hover:bg-destructive/10"
                      }
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </Card>
              </div>
            ))
          ) : (
            <div className="text-center py-12">
              <Key className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-30" />
              <p className="text-muted-foreground">No API keys found</p>
            </div>
          )}
        </div>

        {/* Best Practices */}
        <Card className="p-6 border-border bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            API Key Security Best Practices
          </h3>
          <ul className="space-y-2 text-sm text-foreground">
            <li className="flex gap-2">
              <span className="text-blue-600 dark:text-blue-400">•</span>
              <span>Never commit API keys to version control</span>
            </li>
            <li className="flex gap-2">
              <span className="text-blue-600 dark:text-blue-400">•</span>
              <span>Use environment variables to store sensitive keys</span>
            </li>
            <li className="flex gap-2">
              <span className="text-blue-600 dark:text-blue-400">•</span>
              <span>Rotate keys regularly for security</span>
            </li>
            <li className="flex gap-2">
              <span className="text-blue-600 dark:text-blue-400">•</span>
              <span>Monitor key usage and revoke unused keys</span>
            </li>
          </ul>
        </Card>
      </div>
    </Layout>
  );
}
