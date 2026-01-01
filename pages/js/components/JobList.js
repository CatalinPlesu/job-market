/**
 * JobList Component
 * Grid of job cards with loading and error states
 */

import { JobCard } from './JobCard.js';

export const JobList = {
    view: (vnode) => {
        const { state, actions } = vnode.attrs;
        
        // Loading state
        if (state.loading) {
            return m('.flex.items-center.justify-center.py-20', [
                m('.loading.loading-spinner.loading-lg.text-primary')
            ]);
        }
        
        // Error state
        if (state.error) {
            return m('.alert.alert-error', [
                m('svg.stroke-current.flex-shrink-0.h-6.w-6', {
                    fill: 'none',
                    viewBox: '0 0 24 24'
                }, [
                    m('path', {
                        'stroke-linecap': 'round',
                        'stroke-linejoin': 'round',
                        'stroke-width': '2',
                        d: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
                    })
                ]),
                m('span', state.error)
            ]);
        }
        
        // Empty state
        if (!state.jobs || state.jobs.length === 0) {
            return m('.flex.items-center.justify-center.py-20', [
                m('.text-center', [
                    m('.text-6xl.mb-4', '🔍'),
                    m('h3.text-2xl.font-bold.text-base-content.mb-2', 'No Jobs Found'),
                    m('p.text-base-content.opacity-70.mb-4', 'Try adjusting your filters to see more results'),
                    m('button.btn.btn-primary', {
                        onclick: actions.resetFilters
                    }, 'Reset Filters')
                ])
            ]);
        }
        
        // Jobs grid
        return m('div', [
            // Results summary
            m('.mb-4.text-sm.opacity-70', 
                `Showing ${state.jobs.length} of ${state.totalJobs || state.jobs.length} jobs`
            ),
            
            // Grid of job cards
            m('.grid.grid-cols-1.md:grid-cols-2.gap-4',
                state.jobs.map(job =>
                    m(JobCard, {
                        key: job.id,
                        job: job,
                        onclick: actions.openJobDetail
                    })
                )
            )
        ]);
    }
};
