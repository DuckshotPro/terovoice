/**
 * Error Handler Utilities
 *
 * Centralized error handling and formatting
 */

/**
 * Error types
 */
export const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  AUTHENTICATION: 'AUTHENTICATION_ERROR',
  AUTHORIZATION: 'AUTHORIZATION_ERROR',
  NOT_FOUND: 'NOT_FOUND_ERROR',
  SERVER: 'SERVER_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR',
};

/**
 * Get error type from HTTP status code
 */
export const getErrorType = (status) => {
  if (!status) return ERROR_TYPES.NETWORK;
  if (status === 400) return ERROR_TYPES.VALIDATION;
  if (status === 401) return ERROR_TYPES.AUTHENTICATION;
  if (status === 403) return ERROR_TYPES.AUTHORIZATION;
  if (status === 404) return ERROR_TYPES.NOT_FOUND;
  if (status >= 500) return ERROR_TYPES.SERVER;
  return ERROR_TYPES.UNKNOWN;
};

/**
 * Format error message
 */
export const formatErrorMessage = (error) => {
  if (typeof error === 'string') {
    return error;
  }

  if (error.message) {
    return error.message;
  }

  if (error.data?.message) {
    return error.data.message;
  }

  if (error.data?.error) {
    return error.data.error;
  }

  return 'An unexpected error occurred';
};

/**
 * Handle API error
 */
export const handleApiError = (error) => {
  const formattedError = {
    type: ERROR_TYPES.UNKNOWN,
    message: 'An unexpected error occurred',
    status: null,
    data: null,
  };

  if (error.isNetworkError) {
    formattedError.type = ERROR_TYPES.NETWORK;
    formattedError.message = 'Network error. Please check your connection.';
  } else if (error.status) {
    formattedError.type = getErrorType(error.status);
    formattedError.status = error.status;
    formattedError.message = formatErrorMessage(error);
    formattedError.data = error.data;
  } else {
    formattedError.message = formatErrorMessage(error);
  }

  return formattedError;
};

/**
 * Log error (for debugging)
 */
export const logError = (error, context = '') => {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[Error${context ? ` - ${context}` : ''}]`, error);
  }
};

/**
 * Get user-friendly error message
 */
export const getUserFriendlyMessage = (error) => {
  const formattedError = handleApiError(error);

  const messages = {
    [ERROR_TYPES.NETWORK]: 'Unable to connect. Please check your internet connection.',
    [ERROR_TYPES.VALIDATION]: 'Please check your input and try again.',
    [ERROR_TYPES.AUTHENTICATION]: 'Invalid email or password. Please try again.',
    [ERROR_TYPES.AUTHORIZATION]: 'You do not have permission to perform this action.',
    [ERROR_TYPES.NOT_FOUND]: 'The requested resource was not found.',
    [ERROR_TYPES.SERVER]: 'Server error. Please try again later.',
    [ERROR_TYPES.UNKNOWN]: 'An unexpected error occurred. Please try again.',
  };

  return messages[formattedError.type] || formattedError.message;
};

/**
 * Retry logic for failed requests
 */
export const retryWithBackoff = async (fn, maxRetries = 3, delay = 1000) => {
  let lastError;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (i < maxRetries - 1) {
        await new Promise((resolve) => setTimeout(resolve, delay * Math.pow(2, i)));
      }
    }
  }

  throw lastError;
};

export default {
  ERROR_TYPES,
  getErrorType,
  formatErrorMessage,
  handleApiError,
  logError,
  getUserFriendlyMessage,
  retryWithBackoff,
};
