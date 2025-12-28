import { useClients } from '../../contexts/ClientsContext';
import { Plus, Edit2, Trash2, Phone, MapPin } from 'lucide-react';
import ClientForm from '../../components/clients/ClientForm';

export const Clients = () => {
  const { clients, isLoading, error, createClient, updateClient, deleteClient } = useClients();
  const [showForm, setShowForm] = useState(false);
  const [editingClient, setEditingClient] = useState(null);

  const handleAddClient = async (data) => {
    try {
      await createClient(data);
      setShowForm(false);
    } catch (err) {
      console.error('Failed to create client:', err);
    }
  };

  const handleUpdateClient = async (data) => {
    try {
      await updateClient(editingClient.id, data);
      setEditingClient(null);
      setShowForm(false);
    } catch (err) {
      console.error('Failed to update client:', err);
    }
  };

  const handleDeleteClient = async (id) => {
    if (window.confirm('Are you sure you want to delete this client?')) {
      try {
        await deleteClient(id);
      } catch (err) {
        console.error('Failed to delete client:', err);
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
          <p className="text-gray-600 mt-1">Manage your AI receptionist clients</p>
        </div>
        <button
          onClick={() => {
            setEditingClient(null);
            setShowForm(!showForm);
          }}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          <Plus className="w-5 h-5" />
          Add Client
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {showForm && (
        <ClientForm
          client={editingClient}
          onSubmit={editingClient ? handleUpdateClient : handleAddClient}
          onCancel={() => {
            setShowForm(false);
            setEditingClient(null);
          }}
        />
      )}

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-gray-600">Loading clients...</p>
        </div>
      ) : clients.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <p className="text-gray-600 mb-4">No clients yet</p>
          <button
            onClick={() => setShowForm(true)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Create your first client
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {clients.map((client) => (
            <div
              key={client.id}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{client.name}</h3>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
                    {client.phone && (
                      <div className="flex items-center gap-1">
                        <Phone className="w-4 h-4" />
                        {client.phone}
                      </div>
                    )}
                    {client.profession && (
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {client.profession}
                      </div>
                    )}
                  </div>
                  {client.description && <p className="text-gray-600 mt-2">{client.description}</p>}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setEditingClient(client);
                      setShowForm(true);
                    }}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                  >
                    <Edit2 className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDeleteClient(client.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Clients;
