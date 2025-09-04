import React, { useState, useEffect } from 'react';
import taskService from '../services/taskService';

const TaskForm = ({ isOpen, onClose, onTaskCreated }) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        due_date: '',
        tags: '',
        status: 'To Do',
        priority: 2,
        assigned_to: null
    });
    const [statuses, setStatuses] = useState({});
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen) {
            loadStatuses();
        }
    }, [isOpen]);

    const loadStatuses = async () => {
        try {
            const statusData = await taskService.getTaskStatuses();
            setStatuses(statusData);
            // Set default status to first available status
            if (Object.values(statusData).length > 0) {
                setFormData(prev => ({
                    ...prev,
                    status: Object.values(statusData)[0]
                }));
            }
        } catch (err) {
            console.error('Failed to load statuses:', err);
        }
    };

    const handleChange = (e) => {
        const { name, value, type } = e.target;
        
        setFormData(prev => ({
            ...prev,
            [name]: type === 'number' ? parseInt(value) : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // Prepare task data
            const taskData = {
                ...formData,
                due_date: formData.due_date || null,
                tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag) : [],
                assigned_to: formData.assigned_to || null
            };

            console.log('Creating task with data:', taskData);
            const newTask = await taskService.createTask(taskData);
            
            // Reset form
            setFormData({
                title: '',
                description: '',
                due_date: '',
                tags: '',
                status: Object.values(statuses)[0] || 'To Do',
                priority: 2,
                assigned_to: null
            });

            // Notify parent component
            onTaskCreated(newTask);
            onClose();
            
        } catch (err) {
            console.error('Create task error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setFormData({
            title: '',
            description: '',
            due_date: '',
            tags: '',
            status: Object.values(statuses)[0] || 'To Do',
            priority: 2,
            assigned_to: null
        });
        setError('');
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-container">
                <div className="modal-header">
                    <h2>Add New Task</h2>
                    <button 
                        className="modal-close-btn"
                        onClick={handleClose}
                        type="button"
                    >
                        ×
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="task-form">
                    {error && <div className="error">{error}</div>}

                    <div className="form-group">
                        <label htmlFor="title">Title *</label>
                        <input
                            type="text"
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            required
                            placeholder="Enter task title"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="description">Description</label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows="3"
                            placeholder="Enter task description"
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="status">Status *</label>
                            <select
                                id="status"
                                name="status"
                                value={formData.status}
                                onChange={handleChange}
                                required
                            >
                                {Object.entries(statuses).map(([key, value]) => (
                                    <option key={key} value={value}>{value}</option>
                                ))}
                            </select>
                        </div>

                        <div className="form-group">
                            <label htmlFor="priority">Priority *</label>
                            <select
                                id="priority"
                                name="priority"
                                value={formData.priority}
                                onChange={handleChange}
                                required
                            >
                                <option value={1}>High</option>
                                <option value={2}>Medium</option>
                                <option value={3}>Low</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="due_date">Due Date</label>
                        <input
                            type="datetime-local"
                            id="due_date"
                            name="due_date"
                            value={formData.due_date}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="tags">Tags</label>
                        <input
                            type="text"
                            id="tags"
                            name="tags"
                            value={formData.tags}
                            onChange={handleChange}
                            placeholder="Enter tags separated by commas (e.g., urgent, work, personal)"
                        />
                        <small className="form-help">Separate multiple tags with commas</small>
                    </div>

                    <div className="form-actions">
                        <button 
                            type="button" 
                            className="btn btn-secondary"
                            onClick={handleClose}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                        <button 
                            type="submit" 
                            className="btn btn-primary"
                            disabled={loading || !formData.title.trim()}
                        >
                            {loading ? 'Creating...' : 'Create Task'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TaskForm;