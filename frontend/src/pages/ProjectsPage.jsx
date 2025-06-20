import React, { useState } from 'react';
import styled from 'styled-components';
import { FiSearch, FiFilter, FiGrid, FiList } from 'react-icons/fi';
import { useProjects, useMetadata, usePagination } from '../hooks/useApi';
import ProjectCard from '../components/ProjectCard/ProjectCard';
import Skeleton from 'react-loading-skeleton';

const Container = styled.div`
  width: 100%;
  padding: 0 2rem;
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
`;

const PageHeader = styled.div`
  margin-bottom: 2rem;
`;

const PageTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 0.5rem;
`;

const PageSubtitle = styled.p`
  font-size: 1.1rem;
  color: #718096;
`;

const FiltersSection = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
`;

const FiltersRow = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 1rem;
  align-items: center;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const SearchInput = styled.input`
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  
  &::placeholder {
    color: #a0aec0;
  }
`;

const Select = styled.select`
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  background: white;
`;

const ViewToggle = styled.div`
  display: flex;
  background: #f7fafc;
  border-radius: 0.5rem;
  padding: 0.25rem;
`;

const ViewButton = styled.button`
  padding: 0.5rem;
  border-radius: 0.25rem;
  background: ${props => props.active ? '#667eea' : 'transparent'};
  color: ${props => props.active ? 'white' : '#718096'};
  transition: all 0.3s ease;

  &:hover {
    background: ${props => props.active ? '#5a67d8' : '#e2e8f0'};
  }
`;

const ResultsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const ResultsCount = styled.p`
  color: #718096;
  font-size: 0.9rem;
`;

const ProjectsGrid = styled.div`
  display: grid;
  grid-template-columns: ${props => props.viewMode === 'grid' 
    ? 'repeat(auto-fit, minmax(350px, 1fr))' 
    : '1fr'};
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin: 2rem 0;
`;

const PageButton = styled.button`
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  background: ${props => props.active ? '#667eea' : 'white'};
  color: ${props => props.active ? 'white' : '#4a5568'};
  border-radius: 0.5rem;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    background: ${props => props.active ? '#5a67d8' : '#f7fafc'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ProjectsPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedArrondissement, setSelectedArrondissement] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  
  const { page, limit, setPage, nextPage, prevPage } = usePagination(1, 12);
  
  const { data: metadataData } = useMetadata();
  const { data: projectsData, isLoading } = useProjects({
    page,
    limit,
    search: searchTerm || undefined,
    categorie: selectedCategory || undefined,
    arrondissement: selectedArrondissement || undefined,
  });

  const projects = projectsData?.data?.projects || [];
  const pagination = projectsData?.data?.pagination || {};
  const categories = metadataData?.data?.filters?.categories || [];
  const arrondissements = metadataData?.data?.filters?.arrondissements || [];

  const handleProjectClick = (project) => {
    window.location.href = `/projects/${project.id}`;
  };

  const renderPagination = () => {
    const { page: currentPage, pages: totalPages } = pagination;
    if (!totalPages || totalPages <= 1) return null;

    const pageNumbers = [];
    const maxVisible = 5;
    let start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(totalPages, start + maxVisible - 1);
    
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pageNumbers.push(i);
    }

    return (
      <Pagination>
        <PageButton 
          onClick={prevPage} 
          disabled={currentPage <= 1}
        >
          Précédent
        </PageButton>
        
        {start > 1 && (
          <>
            <PageButton onClick={() => setPage(1)}>1</PageButton>
            {start > 2 && <span>...</span>}
          </>
        )}
        
        {pageNumbers.map(pageNum => (
          <PageButton
            key={pageNum}
            active={pageNum === currentPage}
            onClick={() => setPage(pageNum)}
          >
            {pageNum}
          </PageButton>
        ))}
        
        {end < totalPages && (
          <>
            {end < totalPages - 1 && <span>...</span>}
            <PageButton onClick={() => setPage(totalPages)}>{totalPages}</PageButton>
          </>
        )}
        
        <PageButton 
          onClick={nextPage} 
          disabled={currentPage >= totalPages}
        >
          Suivant
        </PageButton>
      </Pagination>
    );
  };

  return (
    <Container>
      <ContentWrapper>
        <PageHeader>
          <PageTitle>Tous les projets</PageTitle>
          <PageSubtitle>
            Explorez l'ensemble des projets de transformation urbaine de Paris
          </PageSubtitle>
        </PageHeader>

        <FiltersSection>
          <FiltersRow>
            <div style={{ position: 'relative' }}>
              <FiSearch 
                style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)',
                  color: '#a0aec0'
                }} 
              />
              <SearchInput
                type="text"
                placeholder="Rechercher un projet..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ paddingLeft: '2.5rem' }}
              />
            </div>

            <Select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">Toutes les catégories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </Select>

            <Select
              value={selectedArrondissement}
              onChange={(e) => setSelectedArrondissement(e.target.value)}
            >
              <option value="">Tous les arrondissements</option>
              {arrondissements.map(arr => (
                <option key={arr} value={arr}>
                  {arr}
                </option>
              ))}
            </Select>

            <ViewToggle>
              <ViewButton
                active={viewMode === 'grid'}
                onClick={() => setViewMode('grid')}
              >
                <FiGrid />
              </ViewButton>
              <ViewButton
                active={viewMode === 'list'}
                onClick={() => setViewMode('list')}
              >
                <FiList />
              </ViewButton>
            </ViewToggle>
          </FiltersRow>
        </FiltersSection>

        <ResultsHeader>
          <ResultsCount>
            {isLoading ? (
              <Skeleton width={200} />
            ) : (
              `${pagination.total || 0} projet(s) trouvé(s)`
            )}
          </ResultsCount>
        </ResultsHeader>

        <ProjectsGrid viewMode={viewMode}>
          {isLoading ? (
            Array.from({ length: limit }).map((_, index) => (
              <div key={index} style={{ background: 'white', borderRadius: '12px', padding: '1.5rem' }}>
                <Skeleton height={200} style={{ marginBottom: '1rem' }} />
                <Skeleton height={20} style={{ marginBottom: '0.5rem' }} />
                <Skeleton height={60} style={{ marginBottom: '1rem' }} />
                <Skeleton height={16} count={3} />
              </div>
            ))
          ) : projects.length > 0 ? (
            projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onClick={handleProjectClick}
              />
            ))
          ) : (
            <div style={{ 
              gridColumn: '1 / -1', 
              textAlign: 'center', 
              padding: '4rem 2rem',
              background: 'white',
              borderRadius: '1rem'
            }}>
              <FiFilter size={48} style={{ color: '#a0aec0', marginBottom: '1rem' }} />
              <h3 style={{ color: '#4a5568', marginBottom: '0.5rem' }}>
                Aucun projet trouvé
              </h3>
              <p style={{ color: '#718096' }}>
                Essayez de modifier vos critères de recherche
              </p>
            </div>
          )}
        </ProjectsGrid>

        {renderPagination()}
      </ContentWrapper>
    </Container>
  );
};

export default ProjectsPage; 