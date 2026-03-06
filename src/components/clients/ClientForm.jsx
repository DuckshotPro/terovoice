import { useForm } from '../../hooks/useForm';
import { X, Loader } from 'lucide-react';

const validateClientForm = (values) => {
  const errors = {};
  if (!values.name?.trim()) errors.name = 'Name is required';
  if (!values.profession?.trim()) errors.profession = 'Profession is required';
  return errors;
};

export const ClientForm = ({ client, onSubmit, onCancel }) => {
  const { values, errors, touched, handleChange, handleBlur, handleSubmit, isSubmitting } = useForm(
    client || {
      name: '',
      profession: '',
      phone: '',
      description: '',
    },
    onSubmit,
    validateClientForm
  );

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900">
          {client ? 'Edit Client' : 'Add New Client'}
        </h2>
        <button onClick={onCancel} className="text-gray-400 hover:text-gray-600">
          <X className="w-6 h-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Business Name *</label>
            <input
              name="name"
              value={values.name}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="e.g., Dr. Smith's Dental Office"
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                touched.name && errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              disabled={isSubmitting}
            />
            {touched.name && errors.name && (
              <p className="text-sm text-red-600 mt-1">{errors.name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Profession *</label>
            <select
              name="profession"
              value={values.profession}
              onChange={handleChange}
              onBlur={handleBlur}
              className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                touched.profession && errors.profession ? 'border-red-500' : 'border-gray-300'
              }`}
              disabled={isSubmitting}
            >
              <option value="">Select profession</option>
              <option value="dentist">Dentist</option>
              <option value="plumber">Plumber</option>
              <option value="mechanic">Mechanic</option>
              <option value="locksmith">Locksmith</option>
              <option value="massage">Massage Therapist</option>
              <option value="photographer">Photographer</option>
              <option value="realtor">Real Estate Agent</option>
              <option value="tattoo">Tattoo Artist</option>
              <option value="inspector">Home Inspector</option>
              <option value="other">Other</option>
            </select>
            {touched.profession && errors.profession && (
              <p className="text-sm text-red-600 mt-1">{errors.profession}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
            <input
              name="phone"
              type="tel"
              value={values.phone}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="+1 (555) 123-4567"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSubmitting}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              name="location"
              value={values.location || ''}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="City, State"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSubmitting}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            name="description"
            value={values.description}
            onChange={handleChange}
            onBlur={handleBlur}
            placeholder="Brief description of the business..."
            rows="3"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isSubmitting}
          />
        </div>

        <div className="flex gap-3 justify-end">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            disabled={isSubmitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:bg-gray-400"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Client'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ClientForm;
