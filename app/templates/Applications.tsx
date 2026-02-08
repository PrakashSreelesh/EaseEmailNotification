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
  Copy,
  Save,
  X,
  Search,
  Package,
  ExternalLink,
  Eye,
  EyeOff,
} from "lucide-react";
import { toast } from "sonner";

interface Application {
  id: string;
  name: string;
  description: string;
  status: "active" | "inactive";
  apiKey: string;
  webhookUrl?: string;
  createdAt: string;
  owner: string;
  apiKeyExpiry: "never" | "set";
  expiryDate?: string;
}

const mockApplications: Application[] = [
  {
    id: "1",
    name: "Website",
    description: "Main company website application",
    status: "active",
    apiKey: "sk_live_abc123def456",
    webhookUrl: "https://example.com/webhooks",
    createdAt: "2024-01-10",
    owner: "You",
    apiKeyExpiry: "never",
  },
  {
    id: "2",
    name: "Mobile App",
    description: "iOS and Android mobile application",
    status: "active",
    apiKey: "sk_live_xyz789uvw012",
    webhookUrl: "https://api.example.com/webhooks",
    createdAt: "2024-01-12",
    owner: "You",
    apiKeyExpiry: "set",
    expiryDate: "2025-12-31",
  },
  {
    id: "3",
    name: "Admin Dashboard",
    description: "Internal admin panel",
    status: "inactive",
    apiKey: "sk_test_admin123",
    createdAt: "2024-01-15",
    owner: "You",
    apiKeyExpiry: "never",
  },
];

export default function Applications() {
  const [applications, setApplications] = useState<Application[]>(
    mockApplications
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showApiKey, setShowApiKey] = useState<string | null>(null);
  const [editData, setEditData] = useState<Partial<Application>>({});

  const filteredApplications = applications.filter(
    (a) =>
      a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleNewApp = () => {
    setEditData({
      name: "",
      description: "",
      status: "active",
      webhookUrl: "",
      apiKeyExpiry: "never",
      expiryDate: "",
    });
    setSelectedApp(null);
    setIsEditing(true);
  };

  const handleEdit = (app: Application) => {
    setSelectedApp(app);
    setEditData(app);
    setIsEditing(true);
  };

  const handleSave = () => {
    if (!editData.name || !editData.description) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (selectedApp) {
      setApplications(
        applications.map((a) =>
          a.id === selectedApp.id
            ? {
                ...selectedApp,
                ...editData,
              }
            : a
        )
      );
      toast.success("Application updated successfully");
    } else {
      const newApp: Application = {
        id: `app_${Date.now()}`,
        name: editData.name || "",
        description: editData.description || "",
        status: editData.status || "active",
        apiKey: `sk_live_${Math.random().toString(36).substr(2, 16)}`,
        webhookUrl: editData.webhookUrl || "",
        createdAt: new Date().toISOString().split("T")[0],
        owner: "You",
        apiKeyExpiry: (editData.apiKeyExpiry as "never" | "set") || "never",
        expiryDate: editData.expiryDate || "",
      };
      setApplications([...applications, newApp]);
      toast.success("Application created successfully");
    }

    setIsEditing(false);
    setSelectedApp(null);
    setEditData({});
  };

  const handleDelete = (id: string) => {
    setApplications(applications.filter((a) => a.id !== id));
    toast.success("Application deleted");
  };

  const toggleStatus = (app: Application) => {
    const updated = applications.map((a) =>
      a.id === app.id
        ? { ...a, status: a.status === "active" ? "inactive" : "active" }
        : a
    );
    setApplications(updated);
    toast.success(`Application ${app.status === "active" ? "deactivated" : "activated"}`);
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
            <h1 className="text-3xl font-bold text-foreground">
              Applications
            </h1>
            <p className="text-muted-foreground mt-2">
              Manage your connected applications and API keys
            </p>
          </div>
          <Button
            onClick={handleNewApp}
            className="gap-2 btn-primary h-10"
          >
            <Plus className="w-4 h-4" />
            New Application
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search applications..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {!isEditing ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredApplications.length > 0 ? (
              filteredApplications.map((app) => (
                <div
                  key={app.id}
                  className="group cursor-pointer"
                  onClick={() => handleEdit(app)}
                >
                  <Card className="p-6 h-full border-border hover:border-accent transition-all duration-300 hover:shadow-lg hover:-translate-y-1 bg-gradient-to-br from-card to-card/50">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground text-lg">
                          {app.name}
                        </h3>
                        <p className="text-sm text-muted-foreground mt-1">
                          {app.description}
                        </p>
                      </div>
                      <Package className="w-5 h-5 text-muted-foreground group-hover:text-accent transition-colors" />
                    </div>

                    <div className="space-y-4 mb-4">
                      <div>
                        <p className="text-xs text-muted-foreground font-medium mb-2">
                          API KEY
                        </p>
                        <div className="flex items-center gap-2">
                          <code className="text-xs bg-muted rounded px-2 py-1 font-mono flex-1 truncate">
                            {showApiKey === app.id
                              ? app.apiKey
                              : app.apiKey.slice(0, 8) +
                                "•".repeat(app.apiKey.length - 8)}
                          </code>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setShowApiKey(
                                showApiKey === app.id ? null : app.id
                              );
                            }}
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            {showApiKey === app.id ? (
                              <EyeOff className="w-4 h-4" />
                            ) : (
                              <Eye className="w-4 h-4" />
                            )}
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              copyToClipboard(app.apiKey);
                            }}
                            className="text-muted-foreground hover:text-foreground transition-colors"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      <div>
                        <p className="text-xs text-muted-foreground font-medium mb-2">
                          STATUS
                        </p>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleStatus(app);
                          }}
                          className={`text-xs font-semibold px-3 py-1.5 rounded-full transition-all ${
                            app.status === "active"
                              ? "bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300 hover:bg-green-100"
                              : "bg-gray-50 dark:bg-gray-950 text-gray-600 dark:text-gray-400 hover:bg-gray-100"
                          }`}
                        >
                          {app.status === "active" ? "Active" : "Inactive"}
                        </button>
                      </div>

                      <div>
                        <p className="text-xs text-muted-foreground font-medium mb-2">
                          CREATED
                        </p>
                        <p className="text-sm text-foreground">
                          {new Date(app.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-2 border-t border-border pt-4">
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(app);
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
                          handleDelete(app.id);
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
                <Package className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-30" />
                <p className="text-muted-foreground">
                  No applications found
                </p>
              </div>
            )}
          </div>
        ) : (
          /* Editor Panel */
          <Card className="border-border p-6 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-foreground">
                {selectedApp ? "Edit Application" : "Create Application"}
              </h2>
              <button
                onClick={() => {
                  setIsEditing(false);
                  setSelectedApp(null);
                  setEditData({});
                }}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <Label className="text-sm font-medium">
                  Application Name *
                </Label>
                <Input
                  placeholder="e.g., Website"
                  value={editData.name || ""}
                  onChange={(e) =>
                    setEditData({ ...editData, name: e.target.value })
                  }
                  className="mt-1"
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Status</Label>
                <select
                  value={editData.status || "active"}
                  onChange={(e) =>
                    setEditData({
                      ...editData,
                      status: e.target.value as "active" | "inactive",
                    })
                  }
                  className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>

              <div className="lg:col-span-2">
                <Label className="text-sm font-medium">Description *</Label>
                <textarea
                  placeholder="Describe your application..."
                  value={editData.description || ""}
                  onChange={(e) =>
                    setEditData({ ...editData, description: e.target.value })
                  }
                  className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground h-24"
                />
              </div>

              <div className="lg:col-span-2">
                <Label className="text-sm font-medium">Webhook URL</Label>
                <Input
                  placeholder="https://example.com/webhooks"
                  value={editData.webhookUrl || ""}
                  onChange={(e) =>
                    setEditData({ ...editData, webhookUrl: e.target.value })
                  }
                  className="mt-1"
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Optional: URL where we'll send email status updates
                </p>
              </div>

              <div className="lg:col-span-2">
                <Label className="text-sm font-medium mb-3 block">
                  API Key Expiry
                </Label>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      id="expiry-never"
                      name="apiKeyExpiry"
                      value="never"
                      checked={editData.apiKeyExpiry === "never"}
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          apiKeyExpiry: e.target.value as "never" | "set",
                          expiryDate: "",
                        })
                      }
                      className="w-4 h-4 cursor-pointer"
                    />
                    <label htmlFor="expiry-never" className="text-sm cursor-pointer">
                      Never (Default)
                    </label>
                  </div>
                  <div className="flex items-center gap-3">
                    <input
                      type="radio"
                      id="expiry-set"
                      name="apiKeyExpiry"
                      value="set"
                      checked={editData.apiKeyExpiry === "set"}
                      onChange={(e) =>
                        setEditData({
                          ...editData,
                          apiKeyExpiry: e.target.value as "never" | "set",
                        })
                      }
                      className="w-4 h-4 cursor-pointer"
                    />
                    <label htmlFor="expiry-set" className="text-sm cursor-pointer">
                      Set Expiry Date
                    </label>
                  </div>

                  {editData.apiKeyExpiry === "set" && (
                    <div className="ml-7 mt-2">
                      <Input
                        type="date"
                        value={editData.expiryDate || ""}
                        onChange={(e) =>
                          setEditData({
                            ...editData,
                            expiryDate: e.target.value,
                          })
                        }
                        className="mt-1"
                      />
                      <p className="text-xs text-muted-foreground mt-2">
                        Select the date when this API key should expire
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-3 pt-6 border-t border-border">
              <Button
                onClick={handleSave}
                className="gap-2 btn-primary flex-1 h-10"
              >
                <Save className="w-4 h-4" />
                {selectedApp ? "Update" : "Create"} Application
              </Button>
              <Button
                onClick={() => {
                  setIsEditing(false);
                  setSelectedApp(null);
                  setEditData({});
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
