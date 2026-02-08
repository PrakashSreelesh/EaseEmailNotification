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
  Save,
  X,
  Search,
  FileText,
  Zap,
} from "lucide-react";
import { toast } from "sonner";

interface Template {
  id: string;
  name: string;
  subject: string;
  category: string;
  createdAt: string;
  content: string;
  testData: string;
}

const mockTemplates: Template[] = [
  {
    id: "1",
    name: "Welcome Email",
    subject: "Welcome to EmailEase",
    category: "Onboarding",
    createdAt: "2024-01-15",
    content:
      "<h1>Welcome {{firstName}}!</h1><p>We're excited to have you on board.</p>",
    testData: '{"firstName": "John"}',
  },
  {
    id: "2",
    name: "Password Reset",
    subject: "Reset Your Password",
    category: "Security",
    createdAt: "2024-01-12",
    content:
      "<p>Click <a href='{{resetLink}}'>here</a> to reset your password.</p>",
    testData: '{"resetLink": "https://example.com/reset"}',
  },
  {
    id: "3",
    name: "Order Confirmation",
    subject: "Order #{{orderNumber}} Confirmed",
    category: "Commerce",
    createdAt: "2024-01-10",
    content:
      "<p>Thank you {{customerName}} for your order. Total: {{total}}</p>",
    testData: '{"customerName": "Jane", "orderNumber": "12345", "total": "$99"}',
  },
];

export default function Templates() {
  const [templates, setTemplates] = useState<Template[]>(mockTemplates);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(
    null
  );
  const [isEditing, setIsEditing] = useState(false);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [editData, setEditData] = useState<Partial<Template>>({});

  const filteredTemplates = templates.filter(
    (t) =>
      t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleNewTemplate = () => {
    setEditData({
      name: "",
      subject: "",
      category: "General",
      content: "<h1>Untitled Template</h1>",
      testData: "{}",
    });
    setSelectedTemplate(null);
    setIsEditing(true);
  };

  const handleEdit = (template: Template) => {
    setSelectedTemplate(template);
    setEditData(template);
    setIsEditing(true);
  };

  const handleSave = () => {
    if (!editData.name || !editData.subject || !editData.content) {
      toast.error("Please fill in all required fields");
      return;
    }

    if (selectedTemplate) {
      setTemplates(
        templates.map((t) =>
          t.id === selectedTemplate.id
            ? {
                ...selectedTemplate,
                ...editData,
              }
            : t
        )
      );
      toast.success("Template updated successfully");
    } else {
      const newTemplate: Template = {
        id: `temp_${Date.now()}`,
        name: editData.name || "",
        subject: editData.subject || "",
        category: editData.category || "General",
        content: editData.content || "",
        testData: editData.testData || "{}",
        createdAt: new Date().toISOString().split("T")[0],
      };
      setTemplates([...templates, newTemplate]);
      toast.success("Template created successfully");
    }

    setIsEditing(false);
    setSelectedTemplate(null);
    setEditData({});
  };

  const handleDelete = (id: string) => {
    setTemplates(templates.filter((t) => t.id !== id));
    toast.success("Template deleted");
  };

  const renderPreview = (template: Template) => {
    let html = template.content;
    try {
      const data = JSON.parse(template.testData);
      Object.entries(data).forEach(([key, value]) => {
        const regex = new RegExp(`{{${key}}}`, "g");
        html = html.replace(regex, String(value));
      });
    } catch (error) {
      console.error("Invalid test data JSON");
    }
    return html;
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              Email Templates
            </h1>
            <p className="text-muted-foreground mt-2">
              Create and manage your email templates with live preview
            </p>
          </div>
          <Button
            onClick={handleNewTemplate}
            className="gap-2 btn-primary h-10"
          >
            <Plus className="w-4 h-4" />
            New Template
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
          <Input
            placeholder="Search templates by name or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {!isEditing ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.length > 0 ? (
              filteredTemplates.map((template) => (
                <div
                  key={template.id}
                  className="group cursor-pointer"
                  onClick={() => handleEdit(template)}
                >
                  <Card className="p-6 h-full border-border hover:border-accent transition-all duration-300 hover:shadow-lg hover:-translate-y-1 bg-gradient-to-br from-card to-card/50">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-foreground text-lg">
                          {template.name}
                        </h3>
                        <span className="inline-block text-xs font-medium text-primary-foreground bg-primary rounded-full px-2 py-1 mt-2">
                          {template.category}
                        </span>
                      </div>
                      <FileText className="w-5 h-5 text-muted-foreground group-hover:text-accent transition-colors" />
                    </div>

                    <div className="space-y-3 mb-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Subject</p>
                        <p className="text-sm text-foreground truncate">
                          {template.subject}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Created</p>
                        <p className="text-sm text-foreground">
                          {new Date(template.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedTemplate(template);
                          setIsPreviewOpen(true);
                        }}
                        variant="outline"
                        size="sm"
                        className="flex-1 gap-1"
                      >
                        <Eye className="w-3 h-3" />
                        Preview
                      </Button>
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(template.id);
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
                <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-30" />
                <p className="text-muted-foreground">No templates found</p>
              </div>
            )}
          </div>
        ) : (
          /* Editor Panel */
          <Card className="border-border p-6 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-foreground">
                {selectedTemplate ? "Edit Template" : "Create Template"}
              </h2>
              <button
                onClick={() => {
                  setIsEditing(false);
                  setSelectedTemplate(null);
                  setEditData({});
                }}
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Form */}
              <div className="lg:col-span-1 space-y-4">
                <div>
                  <Label className="text-sm font-medium">Template Name *</Label>
                  <Input
                    placeholder="e.g., Welcome Email"
                    value={editData.name || ""}
                    onChange={(e) =>
                      setEditData({ ...editData, name: e.target.value })
                    }
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium">Subject Line *</Label>
                  <Input
                    placeholder="e.g., Welcome {{firstName}}!"
                    value={editData.subject || ""}
                    onChange={(e) =>
                      setEditData({ ...editData, subject: e.target.value })
                    }
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium">Category</Label>
                  <select
                    value={editData.category || "General"}
                    onChange={(e) =>
                      setEditData({ ...editData, category: e.target.value })
                    }
                    className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
                  >
                    <option>General</option>
                    <option>Onboarding</option>
                    <option>Security</option>
                    <option>Commerce</option>
                    <option>Notifications</option>
                  </select>
                </div>

                <div>
                  <Label className="text-sm font-medium">
                    Test Data (JSON)
                  </Label>
                  <textarea
                    value={editData.testData || "{}"}
                    onChange={(e) =>
                      setEditData({ ...editData, testData: e.target.value })
                    }
                    className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground text-xs font-mono h-24"
                    placeholder='{"firstName": "John", "email": "john@example.com"}'
                  />
                </div>
              </div>

              {/* Editor and Preview */}
              <div className="lg:col-span-2 space-y-4">
                <div>
                  <Label className="text-sm font-medium">
                    HTML Content *
                  </Label>
                  <textarea
                    value={editData.content || ""}
                    onChange={(e) =>
                      setEditData({ ...editData, content: e.target.value })
                    }
                    className="mt-1 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground text-sm font-mono h-64"
                    placeholder="<h1>Hello {{firstName}}</h1>"
                  />
                  <p className="text-xs text-muted-foreground mt-2 flex items-center gap-2">
                    <Zap className="w-3 h-3" />
                    Use {"{{variable}}"} syntax for dynamic content
                  </p>
                </div>

                {/* Preview */}
                <div className="border border-border rounded-lg p-4 bg-gradient-to-br from-background to-muted/20">
                  <p className="text-xs font-semibold text-muted-foreground mb-3 uppercase tracking-wide">
                    Live Preview
                  </p>
                  <div className="bg-white text-foreground p-4 rounded border border-border min-h-[200px] prose prose-sm max-w-none">
                    <div
                      dangerouslySetInnerHTML={{
                        __html: renderPreview({
                          content: editData.content || "",
                          testData: editData.testData || "{}",
                          name: "",
                          subject: "",
                          category: "",
                          createdAt: "",
                          id: "",
                        }),
                      }}
                    />
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
                {selectedTemplate ? "Update" : "Create"} Template
              </Button>
              <Button
                onClick={() => {
                  setIsEditing(false);
                  setSelectedTemplate(null);
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

        {/* Preview Modal */}
        {isPreviewOpen && selectedTemplate && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
            <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto border-border">
              <div className="sticky top-0 bg-card border-b border-border p-6 flex items-center justify-between">
                <h3 className="text-xl font-semibold text-foreground">
                  {selectedTemplate.name} - Preview
                </h3>
                <button
                  onClick={() => setIsPreviewOpen(false)}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <p className="text-sm font-semibold text-muted-foreground mb-2">
                    Subject
                  </p>
                  <p className="text-lg text-foreground">
                    {renderPreview(selectedTemplate)}
                  </p>
                </div>
                <div className="border-t border-border pt-4">
                  <p className="text-sm font-semibold text-muted-foreground mb-3">
                    Content
                  </p>
                  <div className="bg-gradient-to-br from-background to-muted/20 p-4 rounded-lg prose prose-sm max-w-none">
                    <div
                      dangerouslySetInnerHTML={{
                        __html: renderPreview(selectedTemplate),
                      }}
                    />
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </Layout>
  );
}
