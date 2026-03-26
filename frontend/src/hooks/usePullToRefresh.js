import { useState, useEffect, useCallback } from 'react';

const usePullToRefresh = (onRefresh) => {
  const [touchStart, setTouchStart] = useState(0);
  const [touchEnd, setTouchEnd] = useState(0);
  const [isPulling, setIsPulling] = useState(false);

  const handleTouchStart = useCallback((e) => {
    setTouchStart(e.touches[0].clientY);
  }, []);

  const handleTouchMove = useCallback((e) => {
    const currentTouch = e.touches[0].clientY;
    const pullDistance = currentTouch - touchStart;
    
    if (pullDistance > 0 && window.scrollY === 0) {
      setIsPulling(true);
      // Could add visual indicator here
    }
  }, [touchStart]);

  const handleTouchEnd = useCallback((e) => {
    setTouchEnd(e.changedTouches[0].clientY);
    
    const pullDistance = touchEnd - touchStart;
    
    if (pullDistance > 100 && window.scrollY === 0) {
      onRefresh();
    }
    
    setIsPulling(false);
    setTouchStart(0);
    setTouchEnd(0);
  }, [touchStart, touchEnd, onRefresh]);

  useEffect(() => {
    const element = document.documentElement || document.body;
    
    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: true });
    element.addEventListener('touchend', handleTouchEnd, { passive: true });
    
    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handleTouchStart, handleTouchMove, handleTouchEnd]);

  return { isPulling };
};

export default usePullToRefresh;
