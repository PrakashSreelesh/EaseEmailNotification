import { useState, useMemo } from "react";
import Layout from "@/components/Layout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Search,
  Calendar,
  Filter,
  Clock,
  CheckCircle2,
  AlertCircle,
  Mail,
  MoreVertical,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

type EmailStatus = "queued" | "sent" | "delivered" | "failed";

interface EmailLog {
  id: string;
  recipient: string;
  subject: string;
  template: string;
  status: EmailStatus;
  sentAt: string;
  deliveredAt?: string;
  error?: string;
  applicationName: string;
}

const mockLogs: EmailLog[] = [
  {
    id: "1",
    recipient: "john@example.com",
    subject: "Welcome to EmailEase",
    template: "Welcome Email",
    status: "delivered",
    sentAt: "2024-01-20 10:30:45",
    deliveredAt: "2024-01-20 10:31:10",
    applicationName: "App 1",
  },
  {
    id: "2",
    recipient: "jane@example.com",
    subject: "Reset Your Password",
    template: "Password Reset",
    status: "sent",
    sentAt: "2024-01-20 10:25:22",
    applicationName: "App 2",
  },
  {
    id: "3",
    recipient: "bob@example.com",
    subject: "Order Confirmation #12345",
    template: "Order Confirmation",
    status: "delivered",
    sentAt: "2024-01-20 10:15:00",
    deliveredAt: "2024-01-20 10:15:45",
    applicationName: "App 1",
  },
  {
    id: "4",
    recipient: "alice@example.com",
    subject: "Account Verification",
    template: "Welcome Email",
    status: "failed",
    sentAt: "2024-01-20 09:45:30",
    error: "Invalid email address",
    applicationName: "App 3",
  },
  {
    id: "5",
    recipient: "mike@example.com",
    subject: "Newsletter - January Edition",
    template: "Newsletter",
    status: "queued",
    sentAt: "2024-01-20 09:30:15",
    applicationName: "App 2",
  },
  {
    id: "6",
    recipient: "sarah@example.com",
    subject: "Special Offer - 30% Off",
    template: "Marketing",
    status: "delivered",
    sentAt: "2024-01-20 09:00:00",
    deliveredAt: "2024-01-20 09:01:30",
    applicationName: "App 1",
  },
  {
    id: "7",
    recipient: "tom@example.com",
    subject: "Payment Confirmation",
    template: "Payment",
    status: "sent",
    sentAt: "2024-01-20 08:45:20",
    applicationName: "App 3",
  },
  {
    id: "8",
    recipient: "lisa@example.com",
    subject: "Account Suspended - Action Required",
    template: "Alert",
    status: "delivered",
    sentAt: "2024-01-20 08:30:00",
    deliveredAt: "2024-01-20 08:30:45",
    applicationName: "App 2",
  },
];

export default function EmailLogs() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<EmailStatus | "all">("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [dateRange, setDateRange] = useState("all");
  const itemsPerPage = 10;

  const filteredLogs = useMemo(() => {
    return mockLogs.filter((log) => {
      const matchesSearch =
        log.recipient.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.template.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus =
        filterStatus === "all" || log.status === filterStatus;

      return matchesSearch && matchesStatus;
    });
  }, [searchTerm, filterStatus]);

  const totalPages = Math.ceil(filteredLogs.length / itemsPerPage);
  const paginatedLogs = filteredLogs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const getStatusConfig = (status: EmailStatus) => {
    const config: Record<
      EmailStatus,
      { icon: React.ReactNode; label: string; color: string; bg: string }
    > = {
      queued: {
        icon: <Clock className="w-4 h-4" />,
        label: "Queued",
        color: "text-yellow-600 dark:text-yellow-400",
        bg: "bg-yellow-50 dark:bg-yellow-950",
      },
      sent: {
        icon: <Mail className="w-4 h-4" />,
        label: "Sent",
        color: "text-blue-600 dark:text-blue-400",
        bg: "bg-blue-50 dark:bg-blue-950",
      },
      delivered: {
        icon: <CheckCircle2 className="w-4 h-4" />,
        label: "Delivered",
        color: "text-green-600 dark:text-green-400",
        bg: "bg-green-50 dark:bg-green-950",
      },
      failed: {
        icon: <AlertCircle className="w-4 h-4" />,
        label: "Failed",
        color: "text-destructive dark:text-red-400",
        bg: "bg-red-50 dark:bg-red-950",
      },
    };
    return config[status];
  };

  const stats = {
    total: mockLogs.length,
    sent: mockLogs.filter((l) => l.status === "sent").length,
    delivered: mockLogs.filter((l) => l.status === "delivered").length,
    failed: mockLogs.filter((l) => l.status === "failed").length,
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground">Email Logs</h1>
          <p className="text-muted-foreground mt-2">
            Track and monitor all email sending activity
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              label: "Total Emails",
              value: stats.total,
              color: "blue",
              icon: <Mail className="w-5 h-5" />,
            },
            {
              label: "Sent",
              value: stats.sent,
              color: "purple",
              icon: <Mail className="w-5 h-5" />,
            },
            {
              label: "Delivered",
              value: stats.delivered,
              color: "green",
              icon: <CheckCircle2 className="w-5 h-5" />,
            },
            {
              label: "Failed",
              value: stats.failed,
              color: "red",
              icon: <AlertCircle className="w-5 h-5" />,
            },
          ].map((stat, idx) => (
            <Card
              key={idx}
              className={`p-6 border-border ${
                stat.color === "blue"
                  ? "bg-blue-50/50 dark:bg-blue-950/20"
                  : stat.color === "green"
                    ? "bg-green-50/50 dark:bg-green-950/20"
                    : stat.color === "red"
                      ? "bg-red-50/50 dark:bg-red-950/20"
                      : "bg-purple-50/50 dark:bg-purple-950/20"
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className="text-2xl font-bold text-foreground mt-2">
                    {stat.value}
                  </p>
                </div>
                <div
                  className={`${
                    stat.color === "blue"
                      ? "text-blue-600 dark:text-blue-400"
                      : stat.color === "green"
                        ? "text-green-600 dark:text-green-400"
                        : stat.color === "red"
                          ? "text-red-600 dark:text-red-400"
                          : "text-purple-600 dark:text-purple-400"
                  }`}
                >
                  {stat.icon}
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Filters */}
        <Card className="p-4 md:p-6 border-border space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-foreground" />
            <h3 className="text-lg font-semibold text-foreground">Filters</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Search
              </label>
              <div className="relative mt-2">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                <Input
                  placeholder="Email, subject, template..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Status
              </label>
              <select
                value={filterStatus}
                onChange={(e) => {
                  setFilterStatus(e.target.value as EmailStatus | "all");
                  setCurrentPage(1);
                }}
                className="mt-2 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
              >
                <option value="all">All Statuses</option>
                <option value="queued">Queued</option>
                <option value="sent">Sent</option>
                <option value="delivered">Delivered</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Date Range
              </label>
              <select
                value={dateRange}
                onChange={(e) => {
                  setDateRange(e.target.value);
                  setCurrentPage(1);
                }}
                className="mt-2 w-full px-3 py-2 rounded-md border border-input bg-background text-foreground"
              >
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 Days</option>
                <option value="month">Last 30 Days</option>
              </select>
            </div>
          </div>

          <div className="text-sm text-muted-foreground">
            Showing {paginatedLogs.length} of {filteredLogs.length} emails
          </div>
        </Card>

        {/* Logs Table - Desktop View */}
        <div className="hidden lg:block border border-border rounded-lg overflow-hidden bg-card animate-in fade-in duration-300">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b border-border">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                    Recipient
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                    Subject
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                    Template
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                    Sent At
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-foreground">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {paginatedLogs.length > 0 ? (
                  paginatedLogs.map((log) => {
                    const statusConfig = getStatusConfig(log.status);
                    return (
                      <tr
                        key={log.id}
                        className="hover:bg-muted/30 transition-colors"
                      >
                        <td className="px-6 py-4">
                          <p className="text-sm font-medium text-foreground">
                            {log.recipient}
                          </p>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-foreground truncate max-w-xs">
                            {log.subject}
                          </p>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-sm text-muted-foreground">
                            {log.template}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div
                            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${statusConfig.color} ${statusConfig.bg}`}
                          >
                            {statusConfig.icon}
                            {statusConfig.label}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-muted-foreground">
                            {log.sentAt}
                          </p>
                        </td>
                        <td className="px-6 py-4">
                          <button className="text-muted-foreground hover:text-foreground transition-colors">
                            <MoreVertical className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center">
                      <p className="text-muted-foreground">
                        No emails found matching your filters
                      </p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Logs Cards - Mobile/Tablet View */}
        <div className="lg:hidden space-y-4 animate-in fade-in duration-300">
          {paginatedLogs.length > 0 ? (
            paginatedLogs.map((log) => {
              const statusConfig = getStatusConfig(log.status);
              return (
                <Card
                  key={log.id}
                  className="p-4 border-border hover:shadow-md transition-all duration-300"
                >
                  <div className="space-y-3">
                    {/* Recipient and Status */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                          Recipient
                        </p>
                        <p className="text-sm font-medium text-foreground truncate">
                          {log.recipient}
                        </p>
                      </div>
                      <div
                        className={`inline-flex flex-shrink-0 items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${statusConfig.color} ${statusConfig.bg}`}
                      >
                        {statusConfig.icon}
                        <span className="hidden sm:inline">
                          {statusConfig.label}
                        </span>
                      </div>
                    </div>

                    {/* Subject */}
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Subject
                      </p>
                      <p className="text-sm text-foreground line-clamp-2">
                        {log.subject}
                      </p>
                    </div>

                    {/* Template and Sent At */}
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                          Template
                        </p>
                        <p className="text-sm text-foreground truncate">
                          {log.template}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                          Sent At
                        </p>
                        <p className="text-sm text-foreground truncate">
                          {log.sentAt}
                        </p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex justify-end pt-2 border-t border-border">
                      <button className="text-muted-foreground hover:text-foreground transition-colors p-2 hover:bg-muted rounded">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </Card>
              );
            })
          ) : (
            <div className="text-center py-8">
              <Mail className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-30" />
              <p className="text-muted-foreground">
                No emails found matching your filters
              </p>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages}
            </p>
            <div className="flex gap-2">
              <Button
                onClick={() =>
                  setCurrentPage((p) => Math.max(1, p - 1))
                }
                disabled={currentPage === 1}
                variant="outline"
                size="sm"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .slice(
                  Math.max(0, currentPage - 2),
                  Math.min(totalPages, currentPage + 1)
                )
                .map((page) => (
                  <Button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    variant={currentPage === page ? "default" : "outline"}
                    size="sm"
                    className={
                      currentPage === page ? "btn-primary" : ""
                    }
                  >
                    {page}
                  </Button>
                ))}
              <Button
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages}
                variant="outline"
                size="sm"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
