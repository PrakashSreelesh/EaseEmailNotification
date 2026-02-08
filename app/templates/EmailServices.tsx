import React, { useState, useMemo } from "react";
import { Plus, Search, MoreVertical, X, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import Layout from "@/components/Layout";

interface EmailService {
  id: string;
  name: string;
  description: string;
  status: "Active" | "Draft" | "Inactive";
  owner: string;
  smtpAccounts: number;
  applications: number;
  createdAt: string;
  mappings: Array<{
    id: string;
    application: string;
    smtpAccount: string;
  }>;
}

const mockServices: EmailService[] = [
  {
    id: "1",
    name: "Marketing Emails",
    description: "Service for marketing campaigns",
    status: "Active",
    owner: "John Doe",
    smtpAccounts: 2,
    applications: 1,
    createdAt: "25/01/2024",
    mappings: [
      { id: "1", application: "User Service", smtpAccount: "Gmail Workspace" },
    ],
  },
  {
    id: "2",
    name: "Transactional Emails",
    description: "Service for transactional messages",
    status: "Active",
    owner: "John Doe",
    smtpAccounts: 1,
    applications: 1,
    createdAt: "25/02/2024",
    mappings: [
      {
        id: "1",
        application: "E-commerce Backend",
        smtpAccount: "Gmail Workspace",
      },
    ],
  },
  {
    id: "3",
    name: "Newsletter Service",
    description: "Service for newsletter distribution",
    status: "Draft",
    owner: "Jane Smith",
    smtpAccounts: 1,
    applications: 1,
    createdAt: "10/03/2024",
    mappings: [
      { id: "1", application: "Newsletter App", smtpAccount: "SendGrid" },
    ],
  },
];

const availableApplications = [
  "User Service",
  "E-commerce Backend",
  "Newsletter App",
  "Admin Dashboard",
  "API Service",
];

const availableSMTPAccounts = [
  "Gmail Workspace",
  "SendGrid",
  "AWS SES",
  "Mailgun",
];

export default function EmailServices() {
  const [services, setServices] = useState<EmailService[]>(mockServices);
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editingService, setEditingService] = useState<EmailService | null>(
    null
  );
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    status: "Draft" as const,
    owner: "",
    mappings: [{ application: "", smtpAccount: "" }],
  });

  const filteredServices = useMemo(() => {
    return services.filter(
      (service) =>
        service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        service.owner.toLowerCase().includes(searchTerm.toLowerCase()) ||
        service.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [services, searchTerm]);

  const handleCreateService = () => {
    if (!formData.name.trim()) {
      toast.error("Service name is required");
      return;
    }
    if (formData.mappings.some((m) => !m.application || !m.smtpAccount)) {
      toast.error("All application mappings must have both fields selected");
      return;
    }

    const newService: EmailService = {
      id: Date.now().toString(),
      name: formData.name,
      description: formData.description,
      status: formData.status,
      owner: formData.owner || "Current User",
      smtpAccounts: formData.mappings.length,
      applications: formData.mappings.length,
      createdAt: new Date().toLocaleDateString("en-GB"),
      mappings: formData.mappings.map((m, i) => ({
        id: `${Date.now()}-${i}`,
        application: m.application,
        smtpAccount: m.smtpAccount,
      })),
    };

    setServices([...services, newService]);
    toast.success("Email service created successfully");
    setIsCreateOpen(false);
    setFormData({
      name: "",
      description: "",
      status: "Draft",
      owner: "",
      mappings: [{ application: "", smtpAccount: "" }],
    });
  };

  const handleEditService = () => {
    if (!formData.name.trim()) {
      toast.error("Service name is required");
      return;
    }
    if (formData.mappings.some((m) => !m.application || !m.smtpAccount)) {
      toast.error("All application mappings must have both fields selected");
      return;
    }

    if (!editingService) return;

    setServices(
      services.map((s) =>
        s.id === editingService.id
          ? {
              ...s,
              name: formData.name,
              description: formData.description,
              status: formData.status,
              owner: formData.owner || s.owner,
              smtpAccounts: formData.mappings.length,
              applications: formData.mappings.length,
              mappings: formData.mappings.map((m, i) => ({
                id: `${Date.now()}-${i}`,
                application: m.application,
                smtpAccount: m.smtpAccount,
              })),
            }
          : s
      )
    );

    toast.success("Email service updated successfully");
    setIsEditOpen(false);
    setEditingService(null);
    setFormData({
      name: "",
      description: "",
      status: "Draft",
      owner: "",
      mappings: [{ application: "", smtpAccount: "" }],
    });
  };

  const handleDeleteService = (id: string) => {
    setServices(services.filter((s) => s.id !== id));
    toast.success("Email service deleted successfully");
  };

  const handleOpenCreate = () => {
    setFormData({
      name: "",
      description: "",
      status: "Draft",
      owner: "",
      mappings: [{ application: "", smtpAccount: "" }],
    });
    setIsCreateOpen(true);
  };

  const handleOpenEdit = (service: EmailService) => {
    setEditingService(service);
    setFormData({
      name: service.name,
      description: service.description,
      status: service.status,
      owner: service.owner,
      mappings: service.mappings.map((m) => ({
        application: m.application,
        smtpAccount: m.smtpAccount,
      })),
    });
    setIsEditOpen(true);
  };

  const addMapping = () => {
    setFormData({
      ...formData,
      mappings: [...formData.mappings, { application: "", smtpAccount: "" }],
    });
  };

  const removeMapping = (index: number) => {
    setFormData({
      ...formData,
      mappings: formData.mappings.filter((_, i) => i !== index),
    });
  };

  const updateMapping = (
    index: number,
    field: "application" | "smtpAccount",
    value: string
  ) => {
    const newMappings = [...formData.mappings];
    newMappings[index] = { ...newMappings[index], [field]: value };
    setFormData({ ...formData, mappings: newMappings });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active":
        return "text-green-600 bg-green-50 border-green-200";
      case "Draft":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "Inactive":
        return "text-gray-600 bg-gray-50 border-gray-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Email Services
            </h1>
            <p className="text-muted-foreground mt-1">
              Manage all email services
            </p>
          </div>
          <Button onClick={handleOpenCreate} className="gap-2 self-start sm:self-auto">
            <Plus className="w-4 h-4" />
            New Email Service
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search email services..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Responsive Card Grid View */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServices.length > 0 ? (
            filteredServices.map((service) => (
              <Card key={service.id} className="p-4 md:p-6 hover:shadow-lg transition-shadow">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground">
                      {service.name}
                    </h3>
                    <p className="text-xs text-muted-foreground">
                      {service.description}
                    </p>
                  </div>
                  <span
                    className={cn(
                      "inline-block px-2 py-1 rounded text-xs font-semibold border",
                      getStatusColor(service.status)
                    )}
                  >
                    {service.status}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-muted-foreground text-xs">Owner</p>
                    <p className="font-medium text-foreground">
                      {service.owner}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs">Created</p>
                    <p className="font-medium text-foreground">
                      {service.createdAt}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs">
                      SMTP Accounts
                    </p>
                    <p className="font-medium text-foreground">
                      {service.smtpAccounts}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs">
                      Applications
                    </p>
                    <p className="font-medium text-foreground">
                      {service.applications}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleOpenEdit(service)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="destructive"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleDeleteService(service.id)}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <Mail className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-30" />
              <p className="text-muted-foreground">
                No email services found
              </p>
            </div>
          )}
        </div>

        {/* Create/Edit Dialog */}
        <Dialog
          open={isCreateOpen || isEditOpen}
          onOpenChange={(open) => {
            if (!open) {
              setIsCreateOpen(false);
              setIsEditOpen(false);
              setEditingService(null);
            }
          }}
        >
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingService ? "Edit" : "New"} Email Service
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* Service Name */}
              <div>
                <label className="text-sm font-medium text-foreground">
                  Service Name
                </label>
                <Input
                  placeholder="Email Verification"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="mt-2"
                />
              </div>

              {/* Description */}
              <div>
                <label className="text-sm font-medium text-foreground">
                  Description (Optional)
                </label>
                <textarea
                  placeholder="User's email verification service"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  className="w-full mt-2 px-3 py-2 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  rows={3}
                />
              </div>

              {/* Status */}
              <div>
                <label className="text-sm font-medium text-foreground">
                  Status
                </label>
                <Select value={formData.status} onValueChange={(value: any) =>
                  setFormData({ ...formData, status: value })
                }>
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Draft">Draft</SelectItem>
                    <SelectItem value="Active">Active</SelectItem>
                    <SelectItem value="Inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Owner */}
              <div>
                <label className="text-sm font-medium text-foreground">
                  Owner
                </label>
                <Input
                  placeholder="John Doe"
                  value={formData.owner}
                  onChange={(e) =>
                    setFormData({ ...formData, owner: e.target.value })
                  }
                  className="mt-2"
                />
              </div>

              {/* Application Mappings */}
              <div>
                <label className="text-sm font-medium text-foreground">
                  Application Mappings
                </label>
                <p className="text-xs text-muted-foreground mt-1 mb-3">
                  Link applications to SMTP configurations for this service.
                </p>

                <div className="space-y-3">
                  {formData.mappings.map((mapping, index) => (
                    <div key={index} className="flex gap-2">
                      <Select
                        value={mapping.application}
                        onValueChange={(value) =>
                          updateMapping(index, "application", value)
                        }
                      >
                        <SelectTrigger className="flex-1">
                          <SelectValue placeholder="Application" />
                        </SelectTrigger>
                        <SelectContent>
                          {availableApplications.map((app) => (
                            <SelectItem key={app} value={app}>
                              {app}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      <Select
                        value={mapping.smtpAccount}
                        onValueChange={(value) =>
                          updateMapping(index, "smtpAccount", value)
                        }
                      >
                        <SelectTrigger className="flex-1">
                          <SelectValue placeholder="SMTP Account" />
                        </SelectTrigger>
                        <SelectContent>
                          {availableSMTPAccounts.map((account) => (
                            <SelectItem key={account} value={account}>
                              {account}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      {formData.mappings.length > 1 && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeMapping(index)}
                          className="px-3"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={addMapping}
                  className="mt-3"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add another mapping
                </Button>
              </div>
            </div>

            {/* Dialog Actions */}
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setIsCreateOpen(false);
                  setIsEditOpen(false);
                  setEditingService(null);
                }}
              >
                Cancel
              </Button>
              <Button
                onClick={
                  editingService ? handleEditService : handleCreateService
                }
                className="gap-2"
              >
                {editingService ? "Update" : "Create"} Service
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </Layout>
  );
}
