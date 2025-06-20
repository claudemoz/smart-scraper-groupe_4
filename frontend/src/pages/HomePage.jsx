import React from 'react';
import styled from 'styled-components';
import { FiRefreshCw, FiPlay } from 'react-icons/fi';
import { useProjects, useStatistics, useAuth, useScraper } from '../hooks/useApi';

const Container = styled.div`
  width: 100%;
  padding: 2rem;
`;


const Hero = styled.section`
  text-align: center;
  padding: 4rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin: -2rem -2rem 2rem -2rem;
  border-radius: 0 0 2rem 2rem;
  position: relative;
`;

const Title = styled.h1`
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 700;
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto 2rem auto;
`;

const AdminActions = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
`;

const ScraperButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.3s ease;
  opacity: ${props => props.disabled ? 0.6 : 1};

  &:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-1px);
  }
`;

const StatsSection = styled.section`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin: 3rem 0;
`;

const StatCard = styled.div`
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  border: 1px solid #e2e8f0;
`;

const StatNumber = styled.div`
  font-size: 2.5rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 0.5rem;
`;

const StatLabel = styled.div`
  color: #64748b;
  font-weight: 500;
`;

const ProjectsSection = styled.section`
  margin-top: 4rem;
`;

const SectionTitle = styled.h2`
  font-size: 2rem;
  margin-bottom: 2rem;
  color: #1e293b;
`;

const ProjectGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
`;

const ProjectCard = styled.div`
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  }
`;

const ProjectContent = styled.div`
  padding: 1.5rem;
`;

const ProjectTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #1e293b;
  line-height: 1.4;
`;

const ProjectMeta = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #64748b;
`;

const ProjectDescription = styled.p`
  color: #64748b;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 1.1rem;
  color: #64748b;
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 0.5rem;
  text-align: center;
  margin: 2rem 0;
`;

const HomePage = () => {
  const { isAuthenticated } = useAuth();
  const { trigger: triggerScraper, isLoading: scraperLoading } = useScraper();
  
  const { data: projectsData, isLoading: projectsLoading, error: projectsError } = useProjects({
    limit: 6,
    sort_by: 'updated_at',
    sort_order: 'DESC'
  });

  const { data: statsData, isLoading: statsLoading, error: statsError } = useStatistics();

  const handleScraperTrigger = () => {
    triggerScraper();
  };

  if (projectsError || statsError) {
    return (
      <Container>
        <ErrorMessage>
          Erreur lors du chargement des données. Veuillez vérifier que l'API est démarrée.
        </ErrorMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Hero>
        <Title>Paris se Transforme</Title>
        <Subtitle>
          Découvrez les projets d'aménagement urbain qui transforment la capitale.
          Explorez les données ouvertes de la Ville de Paris en temps réel.
        </Subtitle>
        
        {isAuthenticated && (
          <AdminActions>
            <ScraperButton
              onClick={handleScraperTrigger}
              disabled={scraperLoading}
            >
              {scraperLoading ? (
                <>
                  <FiRefreshCw className="spin" />
                  Scraper en cours...
                </>
              ) : (
                <>
                  <FiPlay />
                  Actualiser les données
                </>
              )}
            </ScraperButton>
          </AdminActions>
        )}
      </Hero>

      <StatsSection>
        {statsLoading ? (
          <LoadingSpinner>Chargement des statistiques...</LoadingSpinner>
        ) : (
          <>
            <StatCard>
              <StatNumber>{statsData?.data?.general?.totalProjects || 0}</StatNumber>
              <StatLabel>Projets Total</StatLabel>
            </StatCard>
            <StatCard>
              <StatNumber>{statsData?.data?.general?.totalArrondissements || 0}</StatNumber>
              <StatLabel>Arrondissements</StatLabel>
            </StatCard>
            <StatCard>
              <StatNumber>{statsData?.data?.general?.totalCategories || 0}</StatNumber>
              <StatLabel>Catégories</StatLabel>
            </StatCard>
            <StatCard>
              <StatNumber>
                {statsData?.data?.general?.budgetTotal ? 
                  `${(statsData.data.general.budgetTotal / 1000000).toFixed(1)}M€` : 
                  'N/A'
                }
              </StatNumber>
              <StatLabel>Budget Total</StatLabel>
            </StatCard>
          </>
        )}
      </StatsSection>

      <ProjectsSection>
        <SectionTitle>Projets Récents</SectionTitle>
        {projectsLoading ? (
          <LoadingSpinner>Chargement des projets...</LoadingSpinner>
        ) : (
          <ProjectGrid>
            {projectsData?.data?.projects?.slice(0, 6).map((project) => (
              <ProjectCard key={project.id}>
                <ProjectContent>
                  <ProjectTitle>{project.nomProjet}</ProjectTitle>
                  <ProjectMeta>
                    <span>📍 {project.arrondissement}e arr.</span>
                    <span>🏷️ {project.categorie}</span>
                  </ProjectMeta>
                  <ProjectDescription>
                    {project.description || 'Description non disponible'}
                  </ProjectDescription>
                </ProjectContent>
              </ProjectCard>
            ))}
          </ProjectGrid>
        )}
      </ProjectsSection>

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

export default HomePage; 