import React, { useState, useEffect } from 'react';
import userService from '../services/userService';
import taskService from '../services/taskService';

const AssignTaskModal = ({ isOpen, task, onClose, onTaskAssigned }) => {
    const [users, setUsers] = useState([]);
    const [selectedUserId, setSelectedUserId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        if (isOpen) {
            loadUsers();
            // Set current assigned user if task is already assigned
            if (task && task.assigned_to) {
                setSelectedUserId(task.assigned_to);
            } else {
                setSelectedUserId('');
            }
        }
    }, [isOpen, task]);

    const loadUsers = async () => {
        try {
            const userData = await userService.getUsers({ limit: 100 });
            setUsers(userData);
        } catch (err) {
            console.error('Failed to load users:', err);
            setError('Failed to load users');
        }
    };

    const handleAssign = async () => {
        if (!selectedUserId) {
            setError('Please select a user to assign this task to');
            return;
        }

        const taskId = task.task_id || task.task_uuid || task.id;
        if (!taskId) {
            setError('Task ID not found');
            return;
        }

        setLoading(true);
        setError('');

        try {
            console.log('Assigning task:', taskId, 'to user:', selectedUserId);
            const updatedTask = await taskService.assignTask(taskId, selectedUserId);
            
            // Find the assigned user details
            const assignedUser = users.find(user => 
                (user.user_id || user.user_uuid || user.id) === selectedUserId
            );

            onTaskAssigned(updatedTask, assignedUser);
            handleClose();
        } catch (err) {
            console.error('Assign task error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleUnassign = async () => {
        const taskId = task.task_id || task.task_uuid || task.id;
        if (!taskId) {
            setError('Task ID not found');
            return;
        }

        setLoading(true);
        setError('');

        try {
            console.log('Unassigning task:', taskId);
            // Pass null to unassign the task
            const updatedTask = await taskService.assignTask(taskId, null);
            
            onTaskAssigned(updatedTask, null);
            handleClose();
        } catch (err) {
            console.error('Unassign task error:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setSelectedUserId('');
        setSearchTerm('');
        setError('');
        onClose();
    };

    const filteredUsers = users.filter(user =>
        user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getAssignedUser = () => {
        if (!task || !task.assigned_to) return null;
        return users.find(user => 
            (user.user_id || user.user_uuid || user.id) === task.assigned_to
        );
    };

    const assignedUser = getAssignedUser();

    if (!isOpen || !task) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-container assign-task-modal">
                <div className="modal-header">
                    <h2>Assign Task</h2>
                    <button 
                        className="modal-close-btn"
                        onClick={handleClose}
                        type="button"
                    >
                        ×
                    </button>
                </div>

                <div className="assign-task-content">
                    <div className="task-info">
                        <h3>Task: {task.title}</h3>
                        <p className="task-description">{task.description}</p>
                        
                        {assignedUser && (
                            <div className="current-assignment">
                                <strong>Currently assigned to:</strong>
                                <div className="assigned-user-card">
                                    <div className="user-avatar">
                                        {assignedUser.name?.charAt(0) || assignedUser.username?.charAt(0)}
                                    </div>
                                    <div className="user-details">
                                        <div className="user-name">{assignedUser.name}</div>
                                        <div className="user-email">{assignedUser.email}</div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {error && <div className="error">{error}</div>}

                    <div className="user-selection">
                        <div className="search-users">
                            <label htmlFor="user-search">Search Users:</label>
                            <input
                                type="text"
                                id="user-search"
                                placeholder="Search by name, username, or email..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>

                        <div className="users-list">
                            <div className="user-option">
                                <label className="user-option-label">
                                    <input
                                        type="radio"
                                        name="assignedUser"
                                        value=""
                                        checked={selectedUserId === ''}
                                        onChange={(e) => setSelectedUserId(e.target.value)}
                                    />
                                    <div className="user-option-content">
                                        <div className="user-avatar unassigned">
                                            <span>—</span>
                                        </div>
                                        <div className="user-details">
                                            <div className="user-name">Unassigned</div>
                                            <div className="user-email">No user assigned to this task</div>
                                        </div>
                                    </div>
                                </label>
                            </div>

                            {filteredUsers.map(user => {
                                const userId = user.user_id || user.user_uuid || user.id;
                                return (
                                    <div key={userId} className="user-option">
                                        <label className="user-option-label">
                                            <input
                                                type="radio"
                                                name="assignedUser"
                                                value={userId}
                                                checked={selectedUserId === userId}
                                                onChange={(e) => setSelectedUserId(e.target.value)}
                                            />
                                            <div className="user-option-content">
                                                <div className="user-avatar">
                                                    {user.name?.charAt(0) || user.username?.charAt(0)}
                                                </div>
                                                <div className="user-details">
                                                    <div className="user-name">{user.name}</div>
                                                    <div className="user-username">@{user.username}</div>
                                                    <div className="user-email">{user.email}</div>
                                                </div>
                                            </div>
                                        </label>
                                    </div>
                                );
                            })}
                        </div>

                        {filteredUsers.length === 0 && searchTerm && (
                            <div className="no-users-found">
                                No users found matching "{searchTerm}"
                            </div>
                        )}
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
                        
                        {assignedUser && (
                            <button 
                                type="button" 
                                className="btn btn-outline"
                                onClick={handleUnassign}
                                disabled={loading}
                            >
                                {loading ? 'Unassigning...' : 'Unassign Task'}
                            </button>
                        )}
                        
                        <button 
                            type="button" 
                            className="btn btn-primary"
                            onClick={handleAssign}
                            disabled={loading || selectedUserId === task.assigned_to}
                        >
                            {loading ? 'Assigning...' : 'Assign Task'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssignTaskModal;