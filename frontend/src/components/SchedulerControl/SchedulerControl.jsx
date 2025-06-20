import React from 'react';
import styled from 'styled-components';
import { FiClock, FiCalendar, FiRefreshCw, FiCheck } from 'react-icons/fi';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';

const Container = styled.div`
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
`;

const Icon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 0.75rem;
`;

const Title = styled.h3`
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
`;

const ConfigSection = styled.div`
  margin-bottom: 2rem;
`;

const ConfigGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const ConfigItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const ConfigLabel = styled.span`
  font-size: 0.9rem;
  font-weight: 500;
  color: #64748b;
  text-transform: uppercase;
`;

const ConfigValue = styled.span`
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.9rem;
  font-weight: 500;
  
  ${props => props.status === 'active' ? `
    background: #dcfce7;
    color: #16a34a;
  ` : `
    background: #fee2e2;
    color: #dc2626;
  `}
`;

const LogsSection = styled.div`
  margin-top: 2rem;
`;

const LogsHeader = styled.div`
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 1rem;
`;

const LogsTitle = styled.h4`
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
`;

const RefreshButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f8fafc;
  color: #64748b;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;

  &:hover {
    background: #f1f5f9;
    color: #475569;
  }
`;

const LogsContainer = styled.div`
  background: #1e293b;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  max-height: 300px;
  overflow-y: auto;
  line-height: 1.4;
`;

const LogEntry = styled.div`
  margin-bottom: 0.5rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #64748b;
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 0.5rem;
  text-align: center;
`;

const SchedulerControl = () => {
  // Récupérer le statut du scheduler
  const { data: statusData, isLoading: statusLoading, error: statusError, refetch: refetchStatus } = useQuery({
    queryKey: ['scheduler-status'],
    queryFn: () => api.get('/scheduler/status'),
    refetchInterval: 30000, // Refresh toutes les 30 secondes
    staleTime: 10000,
  });

  // Récupérer les logs du scheduler
  const { data: logsData, isLoading: logsLoading, error: logsError, refetch: refetchLogs } = useQuery({
    queryKey: ['scheduler-logs'],
    queryFn: () => api.get('/scheduler/logs?lines=20'),
    refetchInterval: 60000, // Refresh toutes les minutes
    staleTime: 30000,
  });

  const handleRefresh = () => {
    refetchStatus();
    refetchLogs();
  };

  const getFrequencyText = (frequency, time, day) => {
    switch (frequency) {
      case 'hourly':
        return 'Toutes les heures';
      case 'daily':
        return `Tous les jours à ${time}`;
      case 'weekly':
        return `Tous les ${day} à ${time}`;
      default:
        return 'Configuration inconnue';
    }
  };

  const getNextExecution = (frequency, time, day) => {
    const now = new Date();
    const [hours, minutes] = time.split(':').map(Number);
    
    if (frequency === 'hourly') {
      const next = new Date(now);
      next.setMinutes(0, 0, 0);
      next.setHours(next.getHours() + 1);
      return next.toLocaleString('fr-FR');
    }
    
    if (frequency === 'daily') {
      const next = new Date(now);
      next.setHours(hours, minutes, 0, 0);
      if (next <= now) {
        next.setDate(next.getDate() + 1);
      }
      return next.toLocaleString('fr-FR');
    }
    
    if (frequency === 'weekly') {
      const daysOfWeek = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
      const targetDay = daysOfWeek.indexOf(day.toLowerCase());
      const next = new Date(now);
      next.setHours(hours, minutes, 0, 0);
      
      const daysUntilTarget = (targetDay - now.getDay() + 7) % 7;
      if (daysUntilTarget === 0 && next <= now) {
        next.setDate(next.getDate() + 7);
      } else {
        next.setDate(next.getDate() + daysUntilTarget);
      }
      
      return next.toLocaleString('fr-FR');
    }
    
    return 'Calcul impossible';
  };

  if (statusError) {
    return (
      <Container>
        <Header>
          <Icon>
            <FiClock size={20} />
          </Icon>
          <Title>Scheduler Automatique</Title>
        </Header>
        <ErrorMessage>
          Erreur lors du chargement du statut du scheduler.
        </ErrorMessage>
      </Container>
    );
  }

  const config = statusData?.data?.config || {};
  const lastLogs = statusData?.data?.last_log_entries || [];
  const logs = logsData?.data?.logs || [];

  return (
    <Container>
      <Header>
        <Icon>
          <FiClock size={20} />
        </Icon>
        <div>
          <Title>Scheduler Automatique</Title>
          <StatusBadge status="active">
            <FiCheck size={16} />
            Actif
          </StatusBadge>
        </div>
      </Header>

      <ConfigSection>
        {statusLoading ? (
          <LoadingSpinner>Chargement de la configuration...</LoadingSpinner>
        ) : (
          <>
            <ConfigGrid>
              <ConfigItem>
                <ConfigLabel>Fréquence</ConfigLabel>
                <ConfigValue>
                  <FiCalendar size={16} />
                  {getFrequencyText(config.frequency, config.time, config.day)}
                </ConfigValue>
              </ConfigItem>
              
              <ConfigItem>
                <ConfigLabel>Prochaine exécution</ConfigLabel>
                <ConfigValue>
                  <FiClock size={16} />
                  {getNextExecution(config.frequency, config.time, config.day)}
                </ConfigValue>
              </ConfigItem>
            </ConfigGrid>

            {lastLogs.length > 0 && (
              <ConfigItem>
                <ConfigLabel>Dernière activité</ConfigLabel>
                <ConfigValue style={{ fontSize: '0.9rem', color: '#64748b' }}>
                  {lastLogs[lastLogs.length - 1]}
                </ConfigValue>
              </ConfigItem>
            )}
          </>
        )}
      </ConfigSection>

      <LogsSection>
        <LogsHeader>
          <LogsTitle>Logs du Scheduler</LogsTitle>
          <RefreshButton onClick={handleRefresh}>
            <FiRefreshCw size={16} />
            Actualiser
          </RefreshButton>
        </LogsHeader>

        {logsLoading ? (
          <LoadingSpinner>Chargement des logs...</LoadingSpinner>
        ) : logsError ? (
          <ErrorMessage>
            Erreur lors du chargement des logs.
          </ErrorMessage>
        ) : (
          <LogsContainer>
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <LogEntry key={index}>
                  {log.message}
                </LogEntry>
              ))
            ) : (
              <LogEntry>Aucun log disponible</LogEntry>
            )}
          </LogsContainer>
        )}
      </LogsSection>
    </Container>
  );
};

export default SchedulerControl; 