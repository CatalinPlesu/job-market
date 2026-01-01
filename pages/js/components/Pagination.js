/**
 * Pagination Component
 * Navigation controls for paginated job results
 */

export const Pagination = {
    view: (vnode) => {
        const { state, actions } = vnode.attrs;
        const currentPage = state.currentPage || 1;
        const totalPages = state.totalPages || 1;
        
        // Don't show pagination if only one page
        if (totalPages <= 1) {
            return null;
        }
        
        // Calculate visible page numbers
        const getVisiblePages = () => {
            const delta = 2;
            const range = [];
            const rangeWithDots = [];
            let l;
            
            for (let i = 1; i <= totalPages; i++) {
                if (i === 1 || i === totalPages || (i >= currentPage - delta && i <= currentPage + delta)) {
                    range.push(i);
                }
            }
            
            range.forEach(i => {
                if (l) {
                    if (i - l === 2) {
                        rangeWithDots.push(l + 1);
                    } else if (i - l !== 1) {
                        rangeWithDots.push('...');
                    }
                }
                rangeWithDots.push(i);
                l = i;
            });
            
            return rangeWithDots;
        };
        
        const visiblePages = getVisiblePages();
        
        return m('.flex.items-center.justify-center.gap-2.mt-6', [
            // First page button
            m('button.btn.btn-sm', {
                disabled: currentPage === 1,
                onclick: () => actions.goToPage(1)
            }, '«'),
            
            // Previous button
            m('button.btn.btn-sm', {
                disabled: currentPage === 1,
                onclick: () => actions.goToPage(currentPage - 1)
            }, '‹'),
            
            // Page numbers
            visiblePages.map(page => {
                if (page === '...') {
                    return m('span.px-2', '...');
                }
                
                return m('button.btn.btn-sm', {
                    class: page === currentPage ? 'btn-primary' : '',
                    onclick: () => actions.goToPage(page)
                }, page.toString());
            }),
            
            // Next button
            m('button.btn.btn-sm', {
                disabled: currentPage === totalPages,
                onclick: () => actions.goToPage(currentPage + 1)
            }, '›'),
            
            // Last page button
            m('button.btn.btn-sm', {
                disabled: currentPage === totalPages,
                onclick: () => actions.goToPage(totalPages)
            }, '»'),
            
            // Page info
            m('.ml-4.text-sm.opacity-70', 
                `Page ${currentPage} of ${totalPages}`
            )
        ]);
    }
};
