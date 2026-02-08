// Shared Sidebar Logic for EmailEase (Orbit Orange Theme)
document.addEventListener('DOMContentLoaded', function () {
    const userRole = localStorage.getItem('userRole') || 'viewer';
    const userEmail = localStorage.getItem('userEmail') || 'super@easeemail.com';
    const nav = document.getElementById('sidebar-nav');

    if (nav) {
        // Find the sidebar container and update its classes for the new theme
        const sidebarAside = nav.closest('aside');
        if (sidebarAside) {
            sidebarAside.className = "w-72 bg-[#111111] flex flex-col h-screen sticky top-0 border-r border-gray-800";
        }

        const isSuperAdmin = localStorage.getItem('isSuperAdmin') === 'true';
        const isAdmin = localStorage.getItem('isAdmin') === 'true';

        const menuItems = [
            { id: 'dashboard', label: 'Dashboard', icon: '📊', path: '/dashboard' }
        ];

        if (isSuperAdmin) {
            menuItems.push({ id: 'tenants', label: 'Tenant Management', icon: '🏢', path: '/tenants' });
        }

        menuItems.push(
            { id: 'smtp', label: 'SMTP Accounts', icon: '🔌', path: '/smtp-accounts' },
            { id: 'applications', label: 'Applications', icon: '📱', path: '/applications' },
            { id: 'services', label: 'Email Services', icon: '📨', path: '/email-services' },
            { id: 'templates', label: 'Email Templates', icon: '📝', path: '/templates' }
        );

        if (isAdmin || isSuperAdmin) {
            menuItems.push({ id: 'users', label: 'User Management', icon: '👥', path: '/users' });
        }

        menuItems.push(
            { id: 'logs', label: 'Email Logs', icon: '📜', path: '/logs' }
        );

        let html = `
        <div class="p-8 mb-4">
            <div class="flex items-center space-x-3 mb-2">
                <div class="w-10 h-10 bg-[#FF7000] rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/20">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </div>
                <div>
                   <h1 class="text-xl font-bold text-white tracking-tight">EmailEase</h1>
                   <p class="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Admin Console</p>
                </div>
            </div>
        </div>
        <div class="flex-1 px-4 space-y-1 overflow-y-auto">
        `;

        const currentPath = window.location.pathname;

        menuItems.forEach(item => {
            const isActive = currentPath === item.path || (currentPath === '/' && item.path === '/dashboard');
            const activeClass = isActive ? 'bg-[#FF7000] text-white shadow-lg shadow-orange-500/20' : 'text-gray-400 hover:bg-[#1E1E2D] hover:text-white';

            html += `
            <a href="${item.path}" class="flex items-center px-4 py-3.5 rounded-xl transition-all duration-200 group ${activeClass}">
                <span class="mr-3 text-lg">${item.icon}</span>
                <span class="font-medium text-[15px]">${item.label}</span>
                ${isActive ? '<span class="ml-auto w-1 h-4 bg-white/20 rounded-full"></span>' : ''}
            </a>`;
        });

        const isSettingsActive = currentPath === '/settings';

        html += `
        </div>
        <div class="p-4 mt-auto border-t border-gray-800/50 space-y-4">
             <a href="/settings" class="flex items-center px-4 py-3.5 rounded-xl transition-all duration-200 group ${isSettingsActive ? 'bg-[#FF7000] text-white shadow-lg shadow-orange-500/20' : 'text-gray-400 hover:bg-[#1E1E2D] hover:text-white'}">
                <div class="flex items-center space-x-3 w-full">
                    <div class="w-8 h-8 rounded-lg ${isSettingsActive ? 'bg-white/20' : 'bg-orange-500/10'} flex items-center justify-center ${isSettingsActive ? 'text-white' : 'text-orange-500'} font-bold text-xs uppercase">
                        ${userRole[0]}
                    </div>
                    <div class="flex-1 overflow-hidden">
                        <p class="text-[10px] font-bold ${isSettingsActive ? 'text-white' : 'text-orange-500'} uppercase tracking-tighter">${userRole.replace('_', ' ')}</p>
                        <p class="text-xs ${isSettingsActive ? 'text-white/80' : 'text-gray-400'} truncate">${userEmail}</p>
                    </div>
                    <span class="text-lg opacity-40 group-hover:opacity-100 transition-opacity">⚙️</span>
                </div>
             </a>
             <button id="logoutBtn" class="flex items-center justify-center w-full px-4 py-3 bg-white text-gray-900 rounded-xl font-bold text-sm shadow-xl shadow-black/20 hover:bg-gray-100 transition-all border border-gray-200 group">
                <svg class="w-4 h-4 mr-2 text-gray-400 group-hover:text-gray-900 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                Logout
            </button>
        </div>
        `;

        nav.innerHTML = html;

        // Re-attach logout listener
        document.getElementById('logoutBtn').addEventListener('click', function () {
            localStorage.clear();
            window.location.href = '/login';
        });

    }

    // Global Spinner Logic
    const spinnerHtml = `
    <div id="global-spinner" class="fixed inset-0 z-[9999] bg-white/80 flex items-center justify-center hidden backdrop-blur-sm transition-opacity duration-300">
        <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-orange-500"></div>
    </div>
    `;
    document.body.insertAdjacentHTML('beforeend', spinnerHtml);

    let activeRequests = 0;
    const spinnerElement = document.getElementById('global-spinner');

    window.showSpinner = function () {
        activeRequests++;
        spinnerElement.classList.remove('hidden');
    };

    window.hideSpinner = function () {
        activeRequests--;
        if (activeRequests <= 0) {
            activeRequests = 0;
            spinnerElement.classList.add('hidden');
        }
    };

    // Intercept Fetch
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
        showSpinner();
        try {
            const response = await originalFetch(...args);
            return response;
        } catch (error) {
            throw error;
        } finally {
            hideSpinner();
        }
    };

    // Show spinner on page unload (navigation)
    window.addEventListener('beforeunload', () => {
        spinnerElement.classList.remove('hidden');
    });
});
