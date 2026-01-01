/**
 * Header Component
 * Displays site header with stats and search bar
 */

export const Header = {
    view: (vnode) => {
        const { state, actions } = vnode.attrs;
        const stats = state.stats || {};
        
        return m('header.bg-base-100.shadow-sm.border-b', [
            m('.max-w-7xl.mx-auto.px-4.sm:px-6.lg:px-8.py-6', [
                // Title and stats
                m('.flex.flex-col.lg:flex-row.lg:items-center.lg:justify-between.gap-4', [
                    m('div', [
                        m('h1.text-3xl.font-bold.text-base-content', '💼 Moldova Job Market'),
                        m('p.text-base-content.opacity-70.mt-1', 'Discover opportunities across all major job sites'),
                        m('.flex.items-center.gap-4.mt-2.text-sm.opacity-60', [
                            m('span', `📊 ${stats.total_jobs || 0} jobs`),
                            m('span', `🏢 ${stats.companies || 0} companies`),
                            m('span', `📍 ${stats.cities || 0} cities`),
                            m('span', `📅 Updated: ${state.lastUpdated || 'Loading...'}`),
                        ])
                    ]),
                    
                    // Action buttons
                    m('.flex.gap-2', [
                        m('button.btn.btn-ghost.btn-sm', {
                            onclick: actions.resetFilters
                        }, 'Reset Filters'),
                        m('button.btn.btn-primary.btn-sm.lg:hidden', {
                            onclick: actions.toggleSidebar
                        }, state.sidebarOpen ? 'Hide Filters' : 'Show Filters')
                    ])
                ]),
                
                // Search Bar
                m('.mt-4', [
                    m('.form-control', [
                        m('.input-group', [
                            m('input.input.input-bordered.w-full', {
                                type: 'text',
                                placeholder: 'Search jobs by title, company, skills...',
                                value: state.filters.search,
                                oninput: (e) => actions.updateSearch(e.target.value)
                            }),
                            m('button.btn.btn-square', [
                                m('svg.h-5.w-5', {
                                    fill: 'none',
                                    stroke: 'currentColor',
                                    viewBox: '0 0 24 24'
                                }, [
                                    m('path', {
                                        'stroke-linecap': 'round',
                                        'stroke-linejoin': 'round',
                                        'stroke-width': '2',
                                        d: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
                                    })
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ]);
    }
};
