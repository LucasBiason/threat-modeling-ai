import { useState, useEffect, useCallback } from 'react';
import {
  getUnreadNotifications,
  markNotificationRead,
} from '../services/threatModelingService';
import type { NotificationsUnreadResponse } from '../types/analysis';

const POLL_INTERVAL_MS = 10000;

export function useNotifications() {
  const [data, setData] = useState<NotificationsUnreadResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchNotifications = useCallback(async () => {
    try {
      const result = await getUnreadNotifications();
      setData(result);
    } catch {
      setData({ unread_count: 0, notifications: [] });
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  const markRead = useCallback(
    async (id: string) => {
      setLoading(true);
      try {
        await markNotificationRead(id);
        await fetchNotifications();
      } finally {
        setLoading(false);
      }
    },
    [fetchNotifications]
  );

  return { data, loading, refetch: fetchNotifications, markRead };
}
