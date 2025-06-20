import React from 'react';
import styled from 'styled-components';
import { FiPlay, FiRefreshCw, FiClock, FiCheck, FiX, FiAlertCircle } from 'react-icons/fi';
import { useScraper, useScraperStatus } from '../../hooks/useApi';

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
  justify-content: space-between;
  margin-bottom: 2rem;
`;

const Title = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
`;

const StatusBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.9rem;
  font-weight: 500;
  
  ${props => {
    switch (props.status) {
      case 'running':
        return `
          background: #dbeafe;
          color: #1d4ed8;
        `;
      case 'success':
        return `
          background: #dcfce7;
          color: #16a34a;
        `;
      case 'error':
        return `
          background: #fee2e2;
          color: #dc2626;
        `;
      case 'timeout':
        return `
          background: #fef3c7;
          color: #d97706;
        `;
      default:
        return `
          background: #f1f5f9;
          color: #64748b;
        `;
    }
  }}
`;

const StatusSection = styled.div`
  margin-bottom: 2rem;
`;

const StatusGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const StatusCard = styled.div`
  background: #f8fafc;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
`;

const StatusLabel = styled.div`
  font-size: 0.8rem;
  color: #64748b;
  margin-bottom: 0.25rem;
  text-transform: uppercase;
  font-weight: 500;
`;

const StatusValue = styled.div`
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
`;

const ActionSection = styled.div`
  display: flex;
  gap: 1rem;
  align-items: center;
`;

const TriggerButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: ${props => props.disabled ? '#e2e8f0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: ${props => props.disabled ? '#94a3b8' : 'white'};
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const SuccessMessage = styled.div`
  background: #dcfce7;
  color: #16a34a;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const InfoBox = styled.div`
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  color: #0369a1;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 2rem;
  font-size: 0.9rem;
`;

const ScraperControl = () => {
  const { trigger, isLoading, error, resetLimits, isResettingLimits } = useScraper();
  const { data: statusData, isLoading: statusLoading } = useScraperStatus();

  const status = statusData?.data || {};
  const isRunning = status.is_running;
  const lastStatus = status.last_status;
  const lastRun = status.last_run ? new Date(status.last_run).toLocaleString('fr-FR') : 'Jamais';
  const lastError = status.last_error;

  const getStatusIcon = () => {
    if (isRunning) return <FiRefreshCw className="spin" />;
    
    switch (lastStatus) {
      case 'success':
        return <FiCheck />;
      case 'error':
        return <FiX />;
      case 'timeout':
        return <FiClock />;
      default:
        return <FiAlertCircle />;
    }
  };

  const getStatusText = () => {
    if (isRunning) return 'En cours';
    
    switch (lastStatus) {
      case 'success':
        return 'Terminé avec succès';
      case 'error':
        return 'Erreur';
      case 'timeout':
        return 'Timeout';
      default:
        return 'Inactif';
    }
  };

  const handleTrigger = () => {
    trigger();
  };

  const handleResetLimits = () => {
    resetLimits();
  };

  const canTrigger = !isRunning && !isLoading;

  return (
    <Container>
      <Header>
        <Title>Contrôle du Scraper</Title>
        <StatusBadge status={isRunning ? 'running' : lastStatus}>
          {getStatusIcon()}
          {getStatusText()}
        </StatusBadge>
      </Header>

      <InfoBox>
        <FiAlertCircle style={{ marginRight: '0.5rem' }} />
        Le scraper collecte les données depuis l'API Paris OpenData. 
        Cette opération peut prendre quelques minutes selon le volume de données.
      </InfoBox>

      <StatusSection>
        <StatusGrid>
          <StatusCard>
            <StatusLabel>Statut</StatusLabel>
            <StatusValue>
              {statusLoading ? 'Chargement...' : (isRunning ? 'En cours d\'exécution' : 'Arrêté')}
            </StatusValue>
          </StatusCard>
          
          <StatusCard>
            <StatusLabel>Dernière exécution</StatusLabel>
            <StatusValue>{lastRun}</StatusValue>
          </StatusCard>
          
          <StatusCard>
            <StatusLabel>Dernier résultat</StatusLabel>
            <StatusValue>
              {!lastStatus ? 'Aucun' : getStatusText()}
            </StatusValue>
          </StatusCard>
        </StatusGrid>

        {lastError && (
          <ErrorMessage>
            <FiX />
            <div>
              <strong>Dernière erreur :</strong>
              <br />
              {lastError}
            </div>
          </ErrorMessage>
        )}
      </StatusSection>

      <ActionSection>
        <TriggerButton
          onClick={handleTrigger}
          disabled={!canTrigger}
        >
          {isLoading ? (
            <>
              <FiRefreshCw className="spin" />
              Démarrage...
            </>
          ) : (
            <>
              <FiPlay />
              {isRunning ? 'Scraper en cours' : 'Lancer le scraper'}
            </>
          )}
        </TriggerButton>
        
        <TriggerButton
          onClick={handleResetLimits}
          disabled={isResettingLimits}
          style={{ 
            background: isResettingLimits ? '#e2e8f0' : '#dc2626',
            opacity: isResettingLimits ? 0.6 : 1
          }}
        >
          {isResettingLimits ? (
            <>
              <FiRefreshCw className="spin" />
              Réinitialisation...
            </>
          ) : (
            <>
              <FiRefreshCw />
              Réinitialiser les limites
            </>
          )}
        </TriggerButton>
        
        {isRunning && (
          <div style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Le scraper est actuellement en cours d'exécution...
          </div>
        )}
      </ActionSection>

      {error && (
        <ErrorMessage>
          <FiX />
          <div>
            <strong>Erreur :</strong>
            <br />
            {error.response?.data?.error?.message || error.message || 'Erreur inconnue'}
          </div>
        </ErrorMessage>
      )}

      <style jsx>{`
        .spin {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Container>
  );
};

export default ScraperControl; 