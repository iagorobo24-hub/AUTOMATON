import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function Layout({ children, actions }) {
  return (
    <div className="flex min-h-screen bg-[var(--bg-base)]">
      <Sidebar />
      
      <main className="flex-1 flex flex-col min-h-screen md:ml-0">
        {/* Mobile spacer for header */}
        <div className="md:hidden h-14" />
        
        <TopBar actions={actions} />
        
        <div className="flex-1 overflow-auto p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
