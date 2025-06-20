import React from 'react';
import styled from 'styled-components';
import { FiDatabase, FiActivity, FiUsers, FiSettings } from 'react-icons/fi';
import { useAuth, useStatistics, useHealth } from '../hooks/useApi';
import ScraperControl from '../components/ScraperControl/ScraperControl';
import SchedulerControl from '../components/SchedulerControl/SchedulerControl';

const Container = styled.div`
  width: 100%;
  padding: 2rem;
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
`;

const Header = styled.div`
  margin-bottom: 3rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  color: #64748b;
  font-size: 1.1rem;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
`;

const Card = styled.div`
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const CardIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 0.75rem;
`;

const CardTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
`;

const StatItem = styled.div`
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.25rem;
`;

const StatLabel = styled.div`
  font-size: 0.8rem;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 500;
`;

const HealthStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  
  ${props => props.healthy ? `
    background: #dcfce7;
    color: #16a34a;
  ` : `
    background: #fee2e2;
    color: #dc2626;
  `}
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

const ScraperSection = styled.div`
  margin-bottom: 3rem;
`;

const SectionTitle = styled.h2`
  font-size: 1.75rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1.5rem;
`;

const AdminPage = () => {
  const { isAuthenticated } = useAuth();
  const { data: statsData, isLoading: statsLoading, error: statsError } = useStatistics();
  const { data: healthData, isLoading: healthLoading, error: healthError } = useHealth();

  // Redirection si non authentifié
  if (!isAuthenticated) {
    return (
      <Container>
        <ErrorMessage>
          Accès non autorisé. Veuillez vous connecter pour accéder à cette page.
        </ErrorMessage>
      </Container>
    );
  }

  const stats = statsData?.data?.general || {};
  const health = healthData?.data || {};

  return (
    <Container>
      <ContentWrapper>
        <Header>
          <Title>Administration</Title>
          <Subtitle>
            Tableau de bord administrateur pour gérer le système de scraping
          </Subtitle>
        </Header>

        <Grid>
        {/* Statistiques générales */}
        <Card>
          <CardHeader>
            <CardIcon>
              <FiDatabase size={20} />
            </CardIcon>
            <CardTitle>Base de données</CardTitle>
          </CardHeader>
          
          {statsLoading ? (
            <LoadingSpinner>Chargement...</LoadingSpinner>
          ) : statsError ? (
            <ErrorMessage>Erreur de chargement</ErrorMessage>
          ) : (
            <StatGrid>
              <StatItem>
                <StatValue>{stats.totalProjects || 0}</StatValue>
                <StatLabel>Projets</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{stats.totalArrondissements || 0}</StatValue>
                <StatLabel>Arrondissements</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{stats.totalCategories || 0}</StatValue>
                <StatLabel>Catégories</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>
                  {stats.budgetTotal ? 
                    `${(stats.budgetTotal / 1000000).toFixed(1)}M€` : 
                    '0€'
                  }
                </StatValue>
                <StatLabel>Budget total</StatLabel>
              </StatItem>
            </StatGrid>
          )}
        </Card>

        {/* État de l'API */}
        <Card>
          <CardHeader>
            <CardIcon>
              <FiActivity size={20} />
            </CardIcon>
            <CardTitle>État de l'API</CardTitle>
          </CardHeader>
          
          {healthLoading ? (
            <LoadingSpinner>Vérification...</LoadingSpinner>
          ) : healthError ? (
            <HealthStatus healthy={false}>
              <FiActivity />
              API indisponible
            </HealthStatus>
          ) : (
            <div>
              <HealthStatus healthy={health.status === 'healthy'}>
                <FiActivity />
                {health.status === 'healthy' ? 'API opérationnelle' : 'API en erreur'}
              </HealthStatus>
              
              {health.database && (
                <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: '#64748b' }}>
                  Base de données : {health.database.status === 'connected' ? 'Connectée' : 'Déconnectée'}
                  <br />
                  Projets en base : {health.database.projects_count || 0}
                </div>
              )}
            </div>
          )}
        </Card>

        {/* Informations système */}
        <Card>
          <CardHeader>
            <CardIcon>
              <FiSettings size={20} />
            </CardIcon>
            <CardTitle>Système</CardTitle>
          </CardHeader>
          
          <div style={{ fontSize: '0.9rem', color: '#64748b', lineHeight: '1.6' }}>
            <div><strong>Version :</strong> {health.version || '1.0.0'}</div>
            <div><strong>Dernière mise à jour :</strong> {health.timestamp ? new Date(health.timestamp).toLocaleString('fr-FR') : 'N/A'}</div>
            <div><strong>Environnement :</strong> {import.meta.env.MODE || 'development'}</div>
          </div>
        </Card>

        {/* Utilisateurs (placeholder) */}
        <Card>
          <CardHeader>
            <CardIcon>
              <FiUsers size={20} />
            </CardIcon>
            <CardTitle>Utilisateurs</CardTitle>
          </CardHeader>
          
          <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
            <div>Utilisateurs connectés : 1</div>
            <div>Dernière connexion : {new Date().toLocaleString('fr-FR')}</div>
          </div>
        </Card>
      </Grid>

      {/* Section Scraper */}
        <ScraperSection>
          <SectionTitle>Gestion du Scraper</SectionTitle>
          <ScraperControl />
        </ScraperSection>

        {/* Section Scheduler */}
        <ScraperSection>
          <SectionTitle>Gestion du Scheduler</SectionTitle>
          <SchedulerControl />
        </ScraperSection>
      </ContentWrapper>
    </Container>
  );
};

export default AdminPage; 