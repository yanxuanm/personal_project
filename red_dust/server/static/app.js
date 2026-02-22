const { createApp, ref, computed, onMounted, watch } = Vue;

createApp({
    setup() {
        const state = ref({
            tick: 0,
            resources: {
                oxygen: 1000,
                water: 800,
                energy: 500,
                food: 600
            },
            agents: {},
            logs: [],
            history_size: 0,
            game_over: false
        });
        
        const history = ref({
            history: [],
            max_tick: 0
        });
        
        const loading = ref(false);
        const autoRefresh = ref(true);
        const timelineValue = ref(0);
        const showDecisionModal = ref(false);
        const currentDecision = ref(null);
        const notifications = ref([]);
        const soundEnabled = ref(false);
        let refreshInterval = null;
        let notificationId = 0;
        
        const prevState = ref({
            pending_decisions: [],
            missions: [],
            missionStatuses: {}
        });
        
        const agentRoles = {
            'Commander Chen': 'COMMANDER',
            'Engineer Tanaka': 'ENGINEER',
            'Dr. Rodriguez': 'MEDICAL OFFICER',
            'Botanist Schmidt': 'BIOLOGIST',
            'Pilot Okafor': 'PILOT/INTEL'
        };
        
        const specializationInfo = {
            'commander': { icon: '⭐', label: 'COMMANDER', color: 'text-yellow-400' },
            'engineer': { icon: '🔧', label: 'ENGINEER', color: 'text-orange-400' },
            'scientist': { icon: '🔬', label: 'SCIENTIST', color: 'text-blue-400' },
            'explorer': { icon: '🧭', label: 'EXPLORER', color: 'text-green-400' },
            'medic': { icon: '❤️', label: 'MEDIC', color: 'text-red-400' },
            'pilot': { icon: '🚀', label: 'PILOT', color: 'text-purple-400' }
        };
        
        const resourceMaxValues = {
            oxygen: 1000,
            water: 800,
            energy: 500,
            food: 600
        };
        
        const apiBase = window.location.origin.includes('localhost') 
            ? 'http://localhost:8000/api' 
            : '/api';
        
        const fetchState = async () => {
            try {
                const response = await axios.get(`${apiBase}/state`);
                state.value = response.data;
                timelineValue.value = state.value.tick;
                
                if (state.value.pending_decisions && state.value.pending_decisions.length > 0) {
                    currentDecision.value = state.value.pending_decisions[0];
                    showDecisionModal.value = true;
                }
                
                checkForChanges();
            } catch (error) {
                console.error('Error fetching state:', error);
            }
        };
        
        const fetchHistory = async () => {
            try {
                const response = await axios.get(`${apiBase}/history`);
                history.value = response.data;
            } catch (error) {
                console.error('Error fetching history:', error);
            }
        };
        
        const nextTick = async () => {
            if (state.value.game_over) return;
            
            loading.value = true;
            try {
                await axios.post(`${apiBase}/next`);
                await fetchState();
                await fetchHistory();
            } catch (error) {
                console.error('Error advancing tick:', error);
                alert('SYSTEM ERROR: ' + error.message);
            } finally {
                loading.value = false;
            }
        };
        
        const resetSimulation = async () => {
            if (!confirm('CONFIRM SYSTEM REBOOT?')) return;
            
            loading.value = true;
            try {
                await axios.post(`${apiBase}/reset`, {});
                await fetchState();
                await fetchHistory();
            } catch (error) {
                console.error('Error resetting simulation:', error);
                alert('REBOOT FAILED: ' + error.message);
            } finally {
                loading.value = false;
            }
        };
        
        const rewindToTick = async (auto = false) => {
            const targetTick = parseInt(timelineValue.value);
            if (targetTick === state.value.tick) return;
            
            if (!auto) {
                if (!confirm(`CONFIRM TEMPORAL REWIND TO T${targetTick}?`)) {
                    timelineValue.value = state.value.tick;
                    return;
                }
            } else {
                const jumpSize = Math.abs(targetTick - state.value.tick);
                if (jumpSize > 10) {
                    if (!confirm(`LARGE TEMPORAL JUMP (${jumpSize} TICKS). CONFIRM?`)) {
                        timelineValue.value = state.value.tick;
                        return;
                    }
                }
            }
            
            loading.value = true;
            try {
                await axios.post(`${apiBase}/rewind/${targetTick}`);
                await fetchState();
                await fetchHistory();
            } catch (error) {
                console.error('Error rewinding:', error);
                alert('TEMPORAL REWIND FAILED: ' + error.message);
                timelineValue.value = state.value.tick;
            } finally {
                loading.value = false;
            }
        };
        
        const onTimelineChange = () => {
            rewindToTick(true);
        };
        
        const toggleAutoRefresh = () => {
            autoRefresh.value = !autoRefresh.value;
            if (autoRefresh.value && !refreshInterval) {
                startAutoRefresh();
            } else if (!autoRefresh.value && refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
            }
        };
        
        const startAutoRefresh = () => {
            if (refreshInterval) clearInterval(refreshInterval);
            refreshInterval = setInterval(() => {
                if (!loading.value) {
                    fetchState();
                    fetchHistory();
                }
            }, 1000);
        };
        
        const getResourcePercentage = (resource) => {
            const max = resourceMaxValues[resource] || 1000;
            const current = state.value.resources[resource] || 0;
            return Math.min(100, (current / max) * 100);
        };
        
        const formatNumber = (num) => {
            return parseFloat(num).toFixed(1);
        };
        
        const getAliveCount = () => {
            return Object.values(state.value.agents).filter(a => a.is_alive).length;
        };
        
        const getAgentColor = (name) => {
            const colors = {
                'Commander Chen': 'bg-blue-900',
                'Engineer Tanaka': 'bg-gray-800',
                'Dr. Rodriguez': 'bg-green-900',
                'Botanist Schmidt': 'bg-emerald-900',
                'Pilot Okafor': 'bg-red-900'
            };
            return colors[name] || 'bg-purple-900';
        };
        
        const getAgentInitial = (name) => {
            return name.split(' ').map(n => n[0]).join('');
        };
        
        const getAgentRole = (name) => {
            return agentRoles[name] || 'CREW MEMBER';
        };
        
        const getAgentSpecialization = (agent) => {
            if (!agent.specialization) return null;
            return specializationInfo[agent.specialization.toLowerCase()] || null;
        };
        
        const getLogColorClass = (log) => {
            if (log.includes('GAME OVER') || log.includes('TRAGEDY') || log.includes('CRITICAL') || log.includes('TERMINATED')) {
                return 'text-red-400';
            } else if (log.includes('DISASTER') || log.includes('WARNING') || log.includes('SABOTAGE')) {
                return 'text-yellow-400';
            } else if (log.includes('RANDOM EVENT')) {
                return 'text-purple-400';
            } else if (log.includes('REPAIR') || log.includes('WORK') || log.includes('RESEARCH')) {
                return 'text-green-400';
            } else {
                return 'text-amber-300';
            }
        };
        
        const extractTick = (log) => {
            const match = log.match(/\[T(\d+)\]/);
            return match ? match[1] : '?';
        };
        
        const getLogTime = (index) => {
            const now = new Date();
            return now.toLocaleTimeString('en-US', { hour12: false });
        };
        
        const getCharProgressBar = (percentage) => {
            const bars = 20;
            const filled = Math.round((percentage / 100) * bars);
            const empty = bars - filled;
            return '[' + '█'.repeat(filled) + '░'.repeat(empty) + ']';
        };
        
        const addNotification = (type, title, message, icon) => {
            const id = ++notificationId;
            notifications.value.push({
                id,
                type,
                title,
                message,
                icon,
                removing: false
            });
            
            if (soundEnabled.value) {
                playNotificationSound(type);
            }
            
            setTimeout(() => {
                dismissNotification(id);
            }, 5000);
        };
        
        const dismissNotification = (id) => {
            const notification = notifications.value.find(n => n.id === id);
            if (notification) {
                notification.removing = true;
                setTimeout(() => {
                    notifications.value = notifications.value.filter(n => n.id !== id);
                }, 300);
            }
        };
        
        const toggleSound = () => {
            soundEnabled.value = !soundEnabled.value;
        };
        
        const playNotificationSound = (type) => {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                if (type === 'decision') {
                    oscillator.frequency.value = 880;
                    oscillator.type = 'square';
                } else if (type === 'mission-new') {
                    oscillator.frequency.value = 660;
                    oscillator.type = 'sine';
                } else if (type === 'mission-complete') {
                    oscillator.frequency.value = 523;
                    oscillator.type = 'sine';
                } else {
                    oscillator.frequency.value = 440;
                    oscillator.type = 'sine';
                }
                
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.3);
            } catch (e) {
                console.log('Audio not supported');
            }
        };
        
        const checkForChanges = () => {
            const current = state.value;
            
            if (current.pending_decisions && current.pending_decisions.length > 0) {
                const newDecisions = current.pending_decisions.filter(
                    d => !prevState.value.pending_decisions.some(pd => pd.id === d.id)
                );
                newDecisions.forEach(decision => {
                    addNotification(
                        'decision',
                        '⚠️ DECISION REQUIRED',
                        decision.title || decision.description || 'A critical decision needs your attention',
                        '⚠️'
                    );
                });
            }
            
            if (current.missions && current.missions.length > 0) {
                const prevMissionIds = prevState.value.missions.map(m => m.id);
                const newMissions = current.missions.filter(m => !prevMissionIds.includes(m.id));
                
                newMissions.forEach(mission => {
                    addNotification(
                        'mission-new',
                        '🚀 NEW MISSION',
                        mission.title + ' - ' + mission.description || 'A new mission has been assigned',
                        '🚀'
                    );
                });
                
                if (prevState.value.missions.length === 0 && current.missions.length > 0) {
                    current.missions.forEach(mission => {
                        addNotification(
                            'mission-new',
                            '🚀 NEW MISSION',
                            mission.title + ' - ' + mission.description || 'A new mission has been assigned',
                            '🚀'
                        );
                    });
                }
                
                current.missions.forEach(mission => {
                    const prevMission = prevState.value.missionStatuses[mission.id];
                    if (mission.status === 'completed' && prevMission !== 'completed') {
                        addNotification(
                            'mission-complete',
                            '✅ MISSION COMPLETE',
                            mission.title || 'Mission completed successfully',
                            '✅'
                        );
                    }
                });
                
                const missionStatuses = {};
                current.missions.forEach(m => {
                    missionStatuses[m.id] = m.status;
                });
                prevState.value.missionStatuses = missionStatuses;
            }
            
            prevState.value.pending_decisions = current.pending_decisions || [];
            prevState.value.missions = current.missions || [];
        };
        
        const resolveDecision = async (optionIndex) => {
            if (!currentDecision.value) return;
            
            loading.value = true;
            try {
                await axios.post(`${apiBase}/decision/resolve`, {
                    decision_id: currentDecision.value.id,
                    option_index: optionIndex
                });
                showDecisionModal.value = false;
                currentDecision.value = null;
                await fetchState();
            } catch (error) {
                console.error('Error resolving decision:', error);
                alert('DECISION FAILED: ' + error.message);
            } finally {
                loading.value = false;
            }
        };
        
        const closeDecisionModal = () => {
        };
        
        const formatReward = (reward) => {
            if (!reward) return '';
            const parts = [];
            for (const [resource, amount] of Object.entries(reward)) {
                const sign = amount > 0 ? '+' : '';
                parts.push(`${sign}${amount} ${resource}`);
            }
            return parts.join(', ');
        };
        
        onMounted(async () => {
            await fetchState();
            await fetchHistory();
            startAutoRefresh();
        });
        
        watch(() => state.value.game_over, (gameOver) => {
            if (gameOver && autoRefresh.value) {
                toggleAutoRefresh();
            }
        });
        
        return {
            state,
            history,
            loading,
            autoRefresh,
            timelineValue,
            showDecisionModal,
            currentDecision,
            notifications,
            soundEnabled,
            fetchState,
            nextTick,
            resetSimulation,
            rewindToTick,
            onTimelineChange,
            toggleAutoRefresh,
            getResourcePercentage,
            formatNumber,
            getAliveCount,
            getAgentColor,
            getAgentInitial,
            getAgentRole,
            getAgentSpecialization,
            getLogColorClass,
            extractTick,
            getLogTime,
            getCharProgressBar,
            resolveDecision,
            closeDecisionModal,
            formatReward,
            dismissNotification,
            toggleSound
        };
    }
}).mount('#app');
