const HomePage = {
    oninit: async () => {
        try {
            state.dbLoading = true;
            await DatabaseManager.init();
            state.dbLoaded = true;
            
            const metadata = await dbApi.getMetadata();
            state.jobsIndex = metadata;
            state.dbLoading = false;
            m.redraw();
        } catch (error) {
            console.error('Failed to load database:', error);
            state.dbError = error;
            state.dbLoading = false;
            m.redraw();
        }
    },
    view: () => m('div', { class: 'container mx-auto px-4 py-8' }, [
        state.dbLoading ? m('div', { class: 'hero min-h-[50vh] bg-base-200 rounded-lg' }, [
            m('div', { class: 'hero-content text-center' }, [
                m('div', { class: 'max-w-md' }, [
                    m('h1', { class: 'text-5xl font-bold mb-4' }, 'Moldova Job Market'),
                    m('div', { class: 'flex flex-col items-center gap-4' }, [
                        m('span', { class: 'loading loading-spinner loading-lg' }),
                        m('p', { class: 'text-sm opacity-70' }, 'Loading job database...')
                    ])
                ])
            ])
        ]) : state.dbError ? m('div', { class: 'hero min-h-[50vh] bg-base-200 rounded-lg' }, [
            m('div', { class: 'hero-content text-center' }, [
                m('div', { class: 'max-w-md' }, [
                    m('h1', { class: 'text-5xl font-bold' }, 'Moldova Job Market'),
                    m('div', { class: 'alert alert-error mt-6' }, [
                        m('span', 'Failed to load database. Please make sure data.db is available in /api/')
                    ])
                ])
            ])
        ]) : m('div', { class: 'hero min-h-[50vh] bg-base-200 rounded-lg' }, [
            m('div', { class: 'hero-content text-center' }, [
                m('div', { class: 'max-w-md' }, [
                    m('h1', { class: 'text-5xl font-bold' }, 'Moldova Job Market'),
                    m('p', { class: 'py-6' }, 'Browse thousands of job opportunities across Moldova. Filter by location, salary, skills, and more.'),
                    state.jobsIndex ? 
                        m('a', { 
                            class: 'stats shadow cursor-pointer hover:shadow-xl transition-shadow justify-center',
                            href: '#!/jobs',
                            oncreate: m.route.link,
                            'aria-label': 'Browse all jobs'
                        }, [
                            m('div', { class: 'stat place-items-center' }, [
                                m('div', { class: 'stat-title' }, 'Total Jobs'),
                                m('div', { class: 'stat-value text-primary' }, state.jobsIndex.total_jobs.toLocaleString()),
                                m('div', { class: 'stat-desc' }, 'Click to browse jobs')
                            ])
                        ])
                    : m(Loading)
                ])
            ])
        ])
    ])
};
