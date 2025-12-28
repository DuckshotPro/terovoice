/**
 * Validation Utilities
 *
 * Common validation functions for forms and data
 */

/**
 * Email validation
 */
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Password validation
 * Requirements:
 * - At least 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one number
 */
export const validatePassword = (password) => {
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
  return passwordRegex.test(password);
};

/**
 * Phone number validation (basic)
 */
export const validatePhone = (phone) => {
  const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
  return phoneRegex.test(phone);
};

/**
 * URL validation
 */
export const validateUrl = (url) => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Required field validation
 */
export const validateRequired = (value) => {
  if (typeof value === 'string') {
    return value.trim().length > 0;
  }
  return value !== null && value !== undefined;
};

/**
 * Min length validation
 */
export const validateMinLength = (value, minLength) => {
  return value && value.length >= minLength;
};

/**
 * Max length validation
 */
export const validateMaxLength = (value, maxLength) => {
  return !value || value.length <= maxLength;
};

/**
 * Login form validation
 */
export const validateLoginForm = (values) => {
  const errors = {};

  if (!validateRequired(values.email)) {
    errors.email = 'Email is required';
  } else if (!validateEmail(values.email)) {
    errors.email = 'Invalid email address';
  }

  if (!validateRequired(values.password)) {
    errors.password = 'Password is required';
  }

  return errors;
};

/**
 * Signup form validation
 */
export const validateSignupForm = (values) => {
  const errors = {};

  if (!validateRequired(values.name)) {
    errors.name = 'Name is required';
  } else if (!validateMinLength(values.name, 2)) {
    errors.name = 'Name must be at least 2 characters';
  }

  if (!validateRequired(values.email)) {
    errors.email = 'Email is required';
  } else if (!validateEmail(values.email)) {
    errors.email = 'Invalid email address';
  }

  if (!validateRequired(values.password)) {
    errors.password = 'Password is required';
  } else if (!validatePassword(values.password)) {
    errors.password =
      'Password must be at least 8 characters with uppercase, lowercase, and numbers';
  }

  if (!validateRequired(values.confirmPassword)) {
    errors.confirmPassword = 'Please confirm your password';
  } else if (values.password !== values.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match';
  }

  return errors;
};

/**
 * Client form validation
 */
export const validateClientForm = (values) => {
  const errors = {};

  if (!validateRequired(values.name)) {
    errors.name = 'Client name is required';
  }

  if (!validateRequired(values.profession)) {
    errors.profession = 'Profession is required';
  }

  if (!validateRequired(values.phone)) {
    errors.phone = 'Phone number is required';
  } else if (!validatePhone(values.phone)) {
    errors.phone = 'Invalid phone number';
  }

  if (values.website && !validateUrl(values.website)) {
    errors.website = 'Invalid website URL';
  }

  return errors;
};

export default {
  validateEmail,
  validatePassword,
  validatePhone,
  validateUrl,
  validateRequired,
  validateMinLength,
  validateMaxLength,
  validateLoginForm,
  validateSignupForm,
  validateClientForm,
};
