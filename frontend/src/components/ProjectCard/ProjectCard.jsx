import React from 'react';
import styled from 'styled-components';
import { FiMapPin, FiCalendar, FiDollarSign, FiExternalLink } from 'react-icons/fi';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

const Card = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
`;

const CardImage = styled.div`
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
  
  ${props => props.hasImage && `
    background-image: url(${props.imageUrl});
    background-size: cover;
    background-position: center;
  `}
`;

const CardContent = styled.div`
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const CardTitle = styled.h3`
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const CardDescription = styled.p`
  margin: 0 0 1rem 0;
  color: #718096;
  font-size: 0.9rem;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
`;

const CardMeta = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: auto;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #4a5568;

  svg {
    color: #667eea;
    flex-shrink: 0;
  }
`;

const CategoryBadge = styled.span`
  display: inline-block;
  background: ${props => getCategoryColor(props.category)};
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  align-self: flex-start;
`;

const StatusBadge = styled.span`
  display: inline-block;
  background: ${props => getStatusColor(props.status)};
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: auto;
`;

const CardFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
  margin-top: 1rem;
`;

const ExternalLink = styled.a`
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #667eea;
  text-decoration: none;
  font-size: 0.85rem;
  font-weight: 500;
  transition: color 0.3s ease;

  &:hover {
    color: #5a67d8;
  }
`;

// Fonctions utilitaires pour les couleurs
const getCategoryColor = (category) => {
  const colors = {
    'Attractivité et emploi': '#48bb78',
    'Logement': '#ed8936',
    'Transport': '#4299e1',
    'Environnement': '#38b2ac',
    'Culture': '#9f7aea',
    'Sport': '#f56565',
    'Éducation': '#ed64a6',
    'Santé': '#4fd1c7'
  };
  return colors[category] || '#718096';
};

const getStatusColor = (status) => {
  const colors = {
    'En cours': '#4299e1',
    'Terminé': '#48bb78',
    'En projet': '#ed8936',
    'Suspendu': '#f56565'
  };
  return colors[status] || '#718096';
};

const formatCurrency = (amount) => {
  if (!amount) return null;
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

const formatDate = (dateString) => {
  if (!dateString) return null;
  try {
    return format(new Date(dateString), 'MMM yyyy', { locale: fr });
  } catch {
    return null;
  }
};

const ProjectCard = ({ project, onClick }) => {
  const {
    nomProjet,
    description,
    categorie,
    arrondissement,
    adresse,
    etatAvancement,
    dateDebut,
    dateFin,
    budget,
    urlParisfr,
    urlPhoto,
    creditPhoto
  } = project;

  const handleClick = () => {
    if (onClick) {
      onClick(project);
    }
  };

  const handleExternalLinkClick = (e) => {
    e.stopPropagation();
  };

  return (
    <Card onClick={handleClick}>
      <CardImage hasImage={!!urlPhoto} imageUrl={urlPhoto}>
        {!urlPhoto && '🏗️'}
        {urlPhoto && creditPhoto && (
          <div style={{
            position: 'absolute',
            bottom: '0.5rem',
            right: '0.5rem',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '0.25rem 0.5rem',
            borderRadius: '0.25rem',
            fontSize: '0.7rem'
          }}>
            © {creditPhoto}
          </div>
        )}
      </CardImage>

      <CardContent>
        <div>
          <CategoryBadge category={categorie}>
            {categorie}
          </CategoryBadge>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <CardTitle>{nomProjet}</CardTitle>
            {etatAvancement && (
              <StatusBadge status={etatAvancement}>
                {etatAvancement}
              </StatusBadge>
            )}
          </div>
        </div>

        <CardDescription>
          {description}
        </CardDescription>

        <CardMeta>
          {adresse && (
            <MetaItem>
              <FiMapPin size={14} />
              <span>{adresse}</span>
              {arrondissement && <span>• {arrondissement}</span>}
            </MetaItem>
          )}

          {(dateDebut || dateFin) && (
            <MetaItem>
              <FiCalendar size={14} />
              <span>
                {dateDebut && formatDate(dateDebut)}
                {dateDebut && dateFin && ' - '}
                {dateFin && formatDate(dateFin)}
              </span>
            </MetaItem>
          )}

          {budget && (
            <MetaItem>
              <FiDollarSign size={14} />
              <span>{formatCurrency(budget)}</span>
            </MetaItem>
          )}
        </CardMeta>

        {urlParisfr && (
          <CardFooter>
            <ExternalLink
              href={urlParisfr}
              target="_blank"
              rel="noopener noreferrer"
              onClick={handleExternalLinkClick}
            >
              <FiExternalLink size={14} />
              Plus d'infos
            </ExternalLink>
          </CardFooter>
        )}
      </CardContent>
    </Card>
  );
};

export default ProjectCard; 