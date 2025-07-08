import { useState, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'timeline_event_timestamps';

export const useEventTimestamps = () => {
  const [eventTimestamps, setEventTimestamps] = useState<Map<string, Date>>(() => {
    const savedData = localStorage.getItem(STORAGE_KEY);
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        const map = new Map();
        Object.entries(parsed).forEach(([key, value]) => {
          map.set(key, new Date(value as string));
        });
        return map;
      } catch (e) {
        console.error("Failed to parse saved timestamps:", e);
        return new Map();
      }
    }
    return new Map();
  });

  useEffect(() => {
    const mapAsObject = Object.fromEntries(
      Array.from(eventTimestamps.entries()).map(([key, date]) => [key, date.toISOString()])
    );
    localStorage.setItem(STORAGE_KEY, JSON.stringify(mapAsObject));
  }, [eventTimestamps]);

  const recordEventTime = useCallback((eventId: string, time: Date = new Date()) => {
    setEventTimestamps(prev => {
      if (!prev.has(eventId)) {
        return new Map(prev.set(eventId, time));
      }
      return prev;
    });
  }, []);

  const getEventTime = useCallback((eventId: string): Date | undefined => {
    return eventTimestamps.get(eventId);
  }, [eventTimestamps]);

  return {
    eventTimestamps,
    recordEventTime,
    getEventTime
  };
};