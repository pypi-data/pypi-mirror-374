import React from 'react';
import { useCookiesContext } from '@/contexts/CookiesContext';
import { sendFetchRequest } from '@/utils';
import type { Result } from '@/shared.types';
import { createSuccess, handleError, toHttpError } from '@/utils/errorHandling';
import logger from '@/logger';

export type Notification = {
  id: number;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  active: boolean;
  created_at: string;
  expires_at?: string;
};

type NotificationContextType = {
  notifications: Notification[];
  dismissedNotifications: number[];
  loading: boolean;
  error: string | null;
  fetchNotifications: () => Promise<Result<Notification[] | null>>;
  dismissNotification: (id: number) => void;
  restoreAllNotifications: () => void;
};

const NotificationContext = React.createContext<NotificationContextType | null>(
  null
);

export const useNotificationContext = () => {
  const context = React.useContext(NotificationContext);
  if (!context) {
    throw new Error(
      'useNotificationContext must be used within a NotificationProvider'
    );
  }
  return context;
};

export const NotificationProvider = ({
  children
}: {
  children: React.ReactNode;
}) => {
  const [notifications, setNotifications] = React.useState<Notification[]>([]);
  const [dismissedNotifications, setDismissedNotifications] = React.useState<
    number[]
  >([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);
  const { cookies } = useCookiesContext();

  // Load dismissed notifications from localStorage
  React.useEffect(() => {
    const dismissed = localStorage.getItem('dismissedNotifications');
    if (dismissed) {
      try {
        setDismissedNotifications(JSON.parse(dismissed));
      } catch {
        logger.warn(
          'Failed to parse dismissed notifications from localStorage'
        );
        localStorage.removeItem('dismissedNotifications');
      }
    }
  }, []);

  const fetchNotifications = React.useCallback(async (): Promise<
    Result<Notification[] | null>
  > => {
    setLoading(true);
    setError(null);

    try {
      const response = await sendFetchRequest(
        '/api/fileglancer/notifications',
        'GET',
        cookies['_xsrf']
      );

      if (response.ok) {
        const data = await response.json();
        if (data?.notifications) {
          return createSuccess(data.notifications as Notification[]);
        }
        // Not an error, just no notifications available
        return createSuccess(null);
      } else {
        throw await toHttpError(response);
      }
    } catch (error) {
      return handleError(error);
    } finally {
      setLoading(false);
    }
  }, [cookies]);

  const dismissNotification = React.useCallback(
    (id: number) => {
      const newDismissed = [...dismissedNotifications, id];
      setDismissedNotifications(newDismissed);
      localStorage.setItem(
        'dismissedNotifications',
        JSON.stringify(newDismissed)
      );
    },
    [dismissedNotifications]
  );

  const restoreAllNotifications = React.useCallback(() => {
    setDismissedNotifications([]);
    localStorage.removeItem('dismissedNotifications');
  }, []);

  // Fetch notifications on mount
  React.useEffect(() => {
    (async function () {
      const result = await fetchNotifications();
      if (result.success) {
        setNotifications(result.data || []);
      } else {
        setError('Failed to load notifications');
      }
    })();
  }, [fetchNotifications]);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        dismissedNotifications,
        loading,
        error,
        fetchNotifications,
        dismissNotification,
        restoreAllNotifications
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;
