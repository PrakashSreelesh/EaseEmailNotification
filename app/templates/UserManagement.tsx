import { useState } from "react";
import Layout from "@/components/Layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Plus,
  Trash2,
  Save,
  X,
  Search,
  Users,
  Mail,
  Shield,
  CheckCircle2,
  MoreVertical,
  Edit2,
} from "lucide-react";
import { toast } from "sonner";

interface StandardUser {
  id: string;
  email: string;
  name: string;
  role: "standard_user";
  status: "active" | "inactive";
  createdAt: string;
  lastLogin?: string;
  applicationsCount: number;
}

const mockUsers: StandardUser[] = [
  {
    id: "1",
    email: "john@example.com",
    name: "John Doe",
    role: "standard_user",
    status: "active",
    createdAt: "2024-01-10",
    lastLogin: "2024-01-20 14:30:00",
    applicationsCount: 3,
  },
  {
    id: "2",
    email: "jane@example.com",
    name: "Jane Smith",
    role: "standard_user",
    status: "active",
    createdAt: "2024-01-12",
    lastLogin: "2024-01-20 10:15:00",
    applicationsCount: 2,
  },
  {
    id: "3",
    email: "bob@example.com",
    name: "Bob Johnson",
    role: "standard_user",
    status: "inactive",
    createdAt: "2024-01-05",
    applicationsCount: 1,
  },
];

export default function UserManagement() {
  const [users, setUsers] = useState<StandardUser[]>(mockUsers);
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [selectedUser, setSelectedUser] = useState<StandardUser | null>(null);
  const [editData, setEditData] = useState<Partial<StandardUser>>({});

  const filteredUsers = users.filter(
    (u) =>
      u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleNewUser = () => {
    setEditData({
      email: "",
      name: "",
      status: "active",
    });
    setSelectedUser(null);
    setIsCreating(true);
  };

  const handleEdit = (user: StandardUser) => {
    setSelectedUser(user);
    setEditData(user);
    setIsCreating(true);
  };

  const handleSave = () => {
    if (!editData.email || !editData.name) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (selectedUser) {
      setUsers(
        users.map((u) =>
          u.id === selectedUser.id
            ? {
                ...selectedUser,
                ...editData,
              }
            : u
        )
      );
      toast.success("User updated successfully");
    } else {
      const newUser: StandardUser = {
        id: `user_${Date.now()}`,
        email: editData.email || "",
        name: editData.name || "",
        role: "standard_user",
        status: editData.status || "active",
        createdAt: new Date().toISOString().split("T")[0],
        applicationsCount: 0,
      };
      setUsers([...users, newUser]);
      toast.success("User created successfully");
    }

    setIsCreating(false);
    setSelectedUser(null);
    setEditData({});
  };

  const handleDeleteUser = (id: string) => {
    setUsers(users.filter((u) => u.id !== id));
    toast.success("User deleted");
  };

  const toggleStatus = (user: StandardUser) => {
    const updated = users.map((u) =>
      u.id === user.id
        ? { ...u, status: u.status === "active" ? "inactive" : "active" }
        : u
    );
    setUsers(updated);
    toast.success(`User ${user.status === "active" ? "deactivated" : "activated"}`);
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              User Management
            </h1>
            <p className="text-muted-foreground mt-2">
              Manage standard user accounts (Super Admin accounts excluded)
            </p>
          </div>
          <Button
            onClick={handleNewUser}
            className="gap-2 btn-primary h-10"
          >
            <Plus className="w-4 h-4" />
            Invite User
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { label: "Total Users", value: users.length, icon: <Users /> },
            {
              label: "Active",
              value: users.filter((u) => u.status === "active").length,
              icon: <CheckCircle2 />,
            },
            {
              label: "Inactive",
              value: users.filter((u) => u.status === "inactive").length,
              icon: <Shield />,
            },
          ].map((stat, idx) => (
            <Card key={idx} className="p-4 border-border">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className="text-2xl font-bold text-foreground mt-1">
                    {stat.value}
                  </p>
                </div>
                <div className="text-primary/50">{stat.icon}</div>
              </div>
            </Card>
          ))}
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search by email or name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Edit Panel */}
        {isCreating && (
          <Card className="border-border p-6 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-foreground">
                {selectedUser ? "Edit User" : "Invite User"}
              </h2>
              <button
                onClick={() => {
                  setIsCreating(false);
                  setSelectedUser(null);
                  setEditData({});
                }}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <Label className="text-sm font-medium">Email Address *</Label>
                <Input
                  type="email"
                  placeholder="user@example.com"
                  value={editData.email || ""}
                  onChange={(e) =>
                    setEditData({ ...editData, email: e.target.value })
                  }
                  className="mt-1"
                  disabled={!!selectedUser}
                />
              </div>

              <div>
                <Label className="text-sm font-medium">Full Name *</Label>
                <Input
                  placeholder="John Doe"
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
            </div>

            <div className="flex gap-3 pt-6 border-t border-border">
              <Button
                onClick={handleSave}
                className="gap-2 btn-primary flex-1 h-10"
              >
                <Save className="w-4 h-4" />
                {selectedUser ? "Update" : "Invite"} User
              </Button>
              <Button
                onClick={() => {
                  setIsCreating(false);
                  setSelectedUser(null);
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

        {/* Users Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in duration-300">
          {filteredUsers.length > 0 ? (
            filteredUsers.map((user) => (
              <Card
                key={user.id}
                className="p-4 border-border hover:shadow-md transition-all duration-300"
              >
                <div className="space-y-3">
                  {/* User Info and Status */}
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-foreground truncate">
                        {user.name}
                      </p>
                      <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1 truncate">
                        <Mail className="w-3 h-3 flex-shrink-0" />
                        {user.email}
                      </p>
                    </div>
                    <button
                      onClick={() => toggleStatus(user)}
                      className={`flex-shrink-0 text-xs font-semibold px-2.5 py-1 rounded-full transition-all ${
                        user.status === "active"
                          ? "bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300 hover:bg-green-100"
                          : "bg-gray-50 dark:bg-gray-950 text-gray-600 dark:text-gray-400 hover:bg-gray-100"
                      }`}
                    >
                      {user.status === "active" ? "Active" : "Inactive"}
                    </button>
                  </div>

                  {/* User Details Grid */}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Applications
                      </p>
                      <p className="text-sm font-medium text-foreground">
                        {user.applicationsCount}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Created
                      </p>
                      <p className="text-sm text-foreground">
                        {new Date(user.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Last Login
                      </p>
                      <p className="text-sm text-foreground">
                        {user.lastLogin || "Never"}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2 border-t border-border">
                    <Button
                      onClick={() => handleEdit(user)}
                      variant="outline"
                      size="sm"
                      className="flex-1 gap-1"
                    >
                      <Edit2 className="w-3 h-3" />
                      <span className="hidden sm:inline">Edit</span>
                    </Button>
                    <Button
                      onClick={() => handleDeleteUser(user.id)}
                      variant="outline"
                      size="sm"
                      className="text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="col-span-full text-center py-8">
              <Users className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-30" />
              <p className="text-muted-foreground">
                No users found matching your search
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
