/**
 * Safe date formatting utilities
 */

/**
 * Safely format a date string to a localized date string
 * @param {string|Date|null|undefined} dateInput - The date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string or fallback
 */
export const formatDate = (dateInput, options = {}) => {
  if (!dateInput) return 'N/A';
  
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      ...options
    };
    
    return date.toLocaleDateString('en-US', defaultOptions);
  } catch (error) {
    console.warn('Date formatting error:', error, 'Input:', dateInput);
    return 'Invalid Date';
  }
};

/**
 * Format date for display in tables (shorter format)
 * @param {string|Date|null|undefined} dateInput - The date to format
 * @returns {string} Formatted date string
 */
export const formatDateShort = (dateInput) => {
  return formatDate(dateInput, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Format date with time for detailed views
 * @param {string|Date|null|undefined} dateInput - The date to format
 * @returns {string} Formatted date and time string
 */
export const formatDateTime = (dateInput) => {
  return formatDate(dateInput, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

/**
 * Format relative time (e.g., "2 hours ago", "Yesterday")
 * @param {string|Date|null|undefined} dateInput - The date to format
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (dateInput) => {
  if (!dateInput) return 'N/A';
  
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    const now = new Date();
    const diffInMs = now - date;
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
    if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    
    return formatDateShort(date);
  } catch (error) {
    console.warn('Relative time formatting error:', error, 'Input:', dateInput);
    return 'Invalid Date';
  }
};

/**
 * Convert date to datetime-local input format
 * @param {string|Date|null|undefined} dateInput - The date to convert
 * @returns {string} Datetime-local formatted string
 */
export const toDateTimeLocal = (dateInput) => {
  if (!dateInput) return '';
  
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) return '';
    
    // Convert to local timezone and format for datetime-local input
    const offset = date.getTimezoneOffset();
    const localDate = new Date(date.getTime() - (offset * 60 * 1000));
    return localDate.toISOString().slice(0, 16);
  } catch (error) {
    console.warn('DateTime local conversion error:', error, 'Input:', dateInput);
    return '';
  }
};

/**
 * Validate if a date string is valid
 * @param {string|Date|null|undefined} dateInput - The date to validate
 * @returns {boolean} True if valid date
 */
export const isValidDate = (dateInput) => {
  if (!dateInput) return false;
  
  try {
    const date = new Date(dateInput);
    return !isNaN(date.getTime());
  } catch (error) {
    return false;
  }
};