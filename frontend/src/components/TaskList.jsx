import React, { useState, useEffect } from 'react';
import taskService from '../services/taskService';
import TaskForm from './TaskForm';
import AssignTaskModal from './AssignTaskModal';

const TaskList = () => {
    const [tasks, setTasks] = useState([]);
    const [statuses, setStatuses] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [deleteLoading, setDeleteLoading] = useState(null);
    const [showTaskForm, setShowTaskForm] = useState(false);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [selectedTask, setSelectedTask] = useState(null);
    const [filters, setFilters] = useState({
        status: '',
        due_date_from: '',
        due_date_to: '',
        assigned_to_me: false
    });

    useEffect(() => {
        loadStatuses();
        loadTasks();
    }, []);

    useEffect(() => {
        loadTasks();
    }, [filters]);

    const loadStatuses = async () => {
        try {
            const statusData = await taskService.getTaskStatuses();
            setStatuses(statusData);
        } catch (err) {
            console.error('Failed to load statuses:', err);
        }
    };

    const loadTasks = async () => {
        setLoading(true);
        setError('');
        try {
            const taskData = await taskService.getTasks(filters);
            console.log('Loaded tasks:', taskData);
            setTasks(taskData);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (filterName, value) => {
        setFilters(prev => ({
            ...prev,
            [filterName]: value
        }));
    };

    const clearFilters = () => {
        setFilters({
            status: '',
            due_date_from: '',
            due_date_to: '',
            assigned_to_me: false
        });
    };

    const handleCompleteTask = async (task) => {
        try {
            const taskId = task.task_id || task.task_uuid || task.id;
            
            if (!taskId) {
                console.error('Task object:', task);
                throw new Error('Task ID not found in task object');
            }
            
            console.log('Completing task:', taskId);
            await taskService.completeTask(taskId);
            loadTasks();
        } catch (err) {
            console.error('Complete task error:', err);
            setError(err.message);
        }
    };

    const handleDeleteTask = async (task) => {
        const taskId = task.task_id || task.task_uuid || task.id;
        
        if (!taskId) {
            console.error('Task object:', task);
            setError('Task ID not found in task object');
            return;
        }

        const confirmDelete = window.confirm(
            `Are you sure you want to delete the task "${task.title}"?\nThis action cannot be undone.`
        );
        
        if (!confirmDelete) {
            return;
        }

        try {
            setDeleteLoading(taskId);
            setError('');
            
            console.log('Deleting task:', taskId);
            await taskService.deleteTask(taskId);
            
            setTasks(prevTasks => prevTasks.filter(t => {
                const tId = t.task_id || t.task_uuid || t.id;
                return tId !== taskId;
            }));
            
        } catch (err) {
            console.error('Delete task error:', err);
            setError(`Failed to delete task: ${err.message}`);
            loadTasks();
        } finally {
            setDeleteLoading(null);
        }
    };

    const handleTaskCreated = (newTask) => {
        console.log('New task created:', newTask);
        setTasks(prevTasks => [newTask, ...prevTasks]);
    };

    const handleAssignTask = (task) => {
        setSelectedTask(task);
        setShowAssignModal(true);
    };

    const handleTaskAssigned = (updatedTask, assignedUser) => {
        console.log('Task assigned:', updatedTask, 'to user:', assignedUser);
        
        // Update the task in the local state
        setTasks(prevTasks => 
            prevTasks.map(task => {
                const taskId = task.task_id || task.task_uuid || task.id;
                const updatedTaskId = updatedTask.task_id || updatedTask.task_uuid || updatedTask.id;
                
                if (taskId === updatedTaskId) {
                    return {
                        ...task,
                        ...updatedTask,
                        assignedUserName: assignedUser?.name || null,
                        assignedUserEmail: assignedUser?.email || null
                    };
                }
                return task;
            })
        );
        
        // Optionally reload tasks to ensure consistency
        // loadTasks();
    };

    const getUserDisplayName = (task) => {
        if (task.assignedUserName) {
            return task.assignedUserName;
        }
        return task.assigned_to ? 'Assigned User' : 'Unassigned';
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'No due date';
        return new Date(dateString).toLocaleDateString();
    };

    const getPriorityColor = (priority) => {
        switch (priority) {
            case 1: return '#e74c3c'; // High - Red
            case 2: return '#f39c12'; // Medium - Orange
            case 3: return '#27ae60'; // Low - Green
            default: return '#95a5a6'; // Default - Gray
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'To Do': return '#3498db';
            case 'In Progress': return '#f39c12';
            case 'Done': return '#27ae60';
            default: return '#95a5a6';
        }
    };

    if (loading) {
        return <div className="loading">Loading tasks...</div>;
    }

    return (
        <div className="task-list-container">
            <div className="task-list-header">
                <h2>My Tasks</h2>
                <button 
                    className="btn btn-primary"
                    onClick={() => setShowTaskForm(true)}
                >
                    Add New Task
                </button>
            </div>

            {/* Filters */}
            <div className="task-filters">
                <div className="filter-group">
                    <label htmlFor="status-filter">Status:</label>
                    <select
                        id="status-filter"
                        value={filters.status}
                        onChange={(e) => handleFilterChange('status', e.target.value)}
                    >
                        <option value="">All Statuses</option>
                        {Object.entries(statuses).map(([key, value]) => (
                            <option key={key} value={value}>{value}</option>
                        ))}
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="date-from">Due Date From:</label>
                    <input
                        type="date"
                        id="date-from"
                        value={filters.due_date_from}
                        onChange={(e) => handleFilterChange('due_date_from', e.target.value)}
                    />
                </div>

                <div className="filter-group">
                    <label htmlFor="date-to">Due Date To:</label>
                    <input
                        type="date"
                        id="date-to"
                        value={filters.due_date_to}
                        onChange={(e) => handleFilterChange('due_date_to', e.target.value)}
                    />
                </div>

                <div className="filter-group">
                    <label>
                        <input
                            type="checkbox"
                            checked={filters.assigned_to_me}
                            onChange={(e) => handleFilterChange('assigned_to_me', e.target.checked)}
                        />
                        Assigned to me only
                    </label>
                </div>

                <button className="btn btn-secondary" onClick={clearFilters}>
                    Clear Filters
                </button>
            </div>

            {error && <div className="error">{error}</div>}

            {/* Task List */}
            <div className="task-list">
                {tasks.length === 0 ? (
                    <div className="no-tasks">No tasks found</div>
                ) : (
                    tasks.map(task => {
                        const taskId = task.task_id || task.task_uuid || task.id;
                        const isDeleting = deleteLoading === taskId;
                        
                        return (
                            <div key={taskId} className={`task-card ${isDeleting ? 'deleting' : ''}`}>
                                <div className="task-header">
                                    <h3 className="task-title">{task.title}</h3>
                                    <div className="task-actions">
                                        {task.status !== 'Done' && (
                                            <button
                                                className="btn btn-success btn-sm"
                                                onClick={() => handleCompleteTask(task)}
                                                disabled={isDeleting}
                                            >
                                                Complete
                                            </button>
                                        )}
                                        <button 
                                            className="btn btn-outline btn-sm"
                                            onClick={() => handleAssignTask(task)}
                                            disabled={isDeleting}
                                        >
                                            Assign
                                        </button>
                                        <button 
                                            className="btn btn-outline btn-sm"
                                            disabled={isDeleting}
                                        >
                                            Edit
                                        </button>
                                        <button 
                                            className="btn btn-danger btn-sm"
                                            onClick={() => handleDeleteTask(task)}
                                            disabled={isDeleting}
                                        >
                                            {isDeleting ? 'Deleting...' : 'Delete'}
                                        </button>
                                    </div>
                                </div>
                                
                                <p className="task-description">{task.description}</p>
                                
                                <div className="task-meta">
                                    <span 
                                        className="task-status"
                                        style={{ backgroundColor: getStatusColor(task.status) }}
                                    >
                                        {task.status}
                                    </span>
                                    
                                    <span 
                                        className="task-priority"
                                        style={{ backgroundColor: getPriorityColor(task.priority) }}
                                    >
                                        Priority: {task.priority === 1 ? 'High' : task.priority === 2 ? 'Medium' : 'Low'}
                                    </span>
                                    
                                    <span className="task-due-date">
                                        Due: {formatDate(task.due_date)}
                                    </span>
                                    
                                    <span className="task-assigned">
                                        👤 {getUserDisplayName(task)}
                                    </span>
                                </div>

                                {task.tags && task.tags.length > 0 && (
                                    <div className="task-tags">
                                        {task.tags.map(tag => (
                                            <span key={tag} className="tag">{tag}</span>
                                        ))}
                                    </div>
                                )}
                                
                                {isDeleting && (
                                    <div className="task-deleting-overlay">
                                        <span>Deleting task...</span>
                                    </div>
                                )}
                            </div>
                        );
                    })
                )}
            </div>

            {/* Modals */}
            <TaskForm
                isOpen={showTaskForm}
                onClose={() => setShowTaskForm(false)}
                onTaskCreated={handleTaskCreated}
            />

            <AssignTaskModal
                isOpen={showAssignModal}
                task={selectedTask}
                onClose={() => {
                    setShowAssignModal(false);
                    setSelectedTask(null);
                }}
                onTaskAssigned={handleTaskAssigned}
            />
        </div>
    );
};

export default TaskList;