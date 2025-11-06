# utils/helpers.py
from database.db_manager import DatabaseManager

def get_user_skills(user_id):
    """Get all skills for a user"""
    db_manager = DatabaseManager()
    query = '''
        SELECT id, skill_name, category, proficiency_level, description
        FROM skills WHERE user_id = %s
    '''
    return db_manager.fetch_all(query, (user_id,))

def search_skills(keyword, category=None):
    """Search for skills in the system"""
    db_manager = DatabaseManager()
    if category:
        query = '''
            SELECT s.id, s.skill_name, s.category, s.proficiency_level, s.description,
                   u.id as user_id, u.full_name, u.email, u.rating
            FROM skills s
            JOIN users u ON s.user_id = u.id
            WHERE (s.skill_name LIKE %s OR s.description LIKE %s) AND s.category = %s
        '''
        return db_manager.fetch_all(query, (f'%{keyword}%', f'%{keyword}%', category))
    else:
        query = '''
            SELECT s.id, s.skill_name, s.category, s.proficiency_level, s.description,
                   u.id as user_id, u.full_name, u.email, u.rating
            FROM skills s
            JOIN users u ON s.user_id = u.id
            WHERE s.skill_name LIKE %s OR s.description LIKE %s
        '''
        return db_manager.fetch_all(query, (f'%{keyword}%', f'%{keyword}%'))

def get_user_exchanges(user_id):
    """Get all individual exchanges for a user (excludes group exchanges)"""
    db_manager = DatabaseManager()
    try:
        query = '''
            SELECT
                e.id,
                e.initiator_id,
                e.recipient_id,
                e.initiator_skill_id,
                e.recipient_skill_id,
                e.status,
                e.created_at,
                e.completed_at,
                u1.full_name as initiator_name,
                u2.full_name as recipient_name,
                COALESCE(s1.skill_name, '[Skill deleted]') as initiator_skill,
                COALESCE(s2.skill_name, '[Skill deleted]') as recipient_skill
            FROM exchanges e
            LEFT JOIN users u1 ON e.initiator_id = u1.id
            LEFT JOIN users u2 ON e.recipient_id = u2.id
            LEFT JOIN skills s1 ON e.initiator_skill_id = s1.id
            LEFT JOIN skills s2 ON e.recipient_skill_id = s2.id
            WHERE (e.initiator_id = %s OR e.recipient_id = %s)
              AND (e.is_group = FALSE OR e.is_group IS NULL)
            ORDER BY e.created_at DESC
        '''
        results = db_manager.fetch_all(query, (user_id, user_id))
        return results
    except Exception as e:
        print(f"Error fetching exchanges: {e}")
        return []

def get_user_profile(user_id):
    """Get detailed user profile"""
    db_manager = DatabaseManager()
    query = '''
        SELECT u.id, u.email, u.full_name, u.bio, u.rating, u.total_exchanges, u.created_at, COUNT(r.id) as rating_count
        FROM users u
        LEFT JOIN ratings r ON u.id = r.rated_user_id
        WHERE u.id = %s
        GROUP BY u.id
    '''
    return db_manager.fetch_one(query, (user_id,))

def send_message(exchange_id, sender_id, recipient_id, message):
    """Send a message in an exchange"""
    db_manager = DatabaseManager()
    query = '''
        INSERT INTO messages (sender_id, recipient_id, exchange_id, message)
        VALUES (%s, %s, %s, %s)
    '''
    db_manager.execute_query(query, (sender_id, recipient_id, exchange_id, message))

def get_messages_for_exchange(exchange_id):
    """Get all messages for an exchange, ordered by timestamp"""
    db_manager = DatabaseManager()
    query = '''
        SELECT m.id, m.sender_id, m.recipient_id, m.message, m.is_read, m.created_at,
               m.attachment_name, m.attachment_data, m.attachment_type,
               u.full_name as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.exchange_id = %s
        ORDER BY m.created_at ASC
    '''
    return db_manager.fetch_all(query, (exchange_id,))

def mark_messages_as_read(exchange_id, user_id):
    """Mark all messages in an exchange as read for a user"""
    db_manager = DatabaseManager()
    query = '''
        UPDATE messages
        SET is_read = TRUE
        WHERE exchange_id = %s AND recipient_id = %s AND is_read = FALSE
    '''
    db_manager.execute_query(query, (exchange_id, user_id))

def get_unread_message_count(user_id):
    """Get total unread messages for a user across all exchanges"""
    db_manager = DatabaseManager()
    query = '''
        SELECT COUNT(*) as unread_count
        FROM messages
        WHERE recipient_id = %s AND is_read = FALSE
    '''
    result = db_manager.fetch_one(query, (user_id,))
    return result['unread_count'] if result else 0

def get_unread_count_for_exchange(exchange_id, user_id):
    """Get unread message count for a specific exchange"""
    db_manager = DatabaseManager()
    query = '''
        SELECT COUNT(*) as unread_count
        FROM messages
        WHERE exchange_id = %s AND recipient_id = %s AND is_read = FALSE
    '''
    result = db_manager.fetch_one(query, (exchange_id, user_id))
    return result['unread_count'] if result else 0

def accept_exchange(exchange_id, user_id):
    """Accept a pending exchange (only recipient can accept)"""
    db_manager = DatabaseManager()
    # First check if user is the recipient
    query = 'SELECT recipient_id FROM exchanges WHERE id = %s'
    exchange = db_manager.fetch_one(query, (exchange_id,))
    if exchange and exchange['recipient_id'] == user_id:
        update_query = 'UPDATE exchanges SET status = %s WHERE id = %s'
        db_manager.execute_query(update_query, ('accepted', exchange_id))
        return True
    return False

def reject_exchange(exchange_id, user_id):
    """Reject a pending exchange (only recipient can reject)"""
    db_manager = DatabaseManager()
    # First check if user is the recipient
    query = 'SELECT recipient_id FROM exchanges WHERE id = %s'
    exchange = db_manager.fetch_one(query, (exchange_id,))
    if exchange and exchange['recipient_id'] == user_id:
        update_query = 'UPDATE exchanges SET status = %s WHERE id = %s'
        db_manager.execute_query(update_query, ('rejected', exchange_id))
        return True
    return False

def complete_exchange(exchange_id, user_id):
    """Mark an accepted exchange as completed"""
    db_manager = DatabaseManager()
    # Check if user is involved in the exchange and it's accepted
    query = '''
        SELECT initiator_id, recipient_id, status
        FROM exchanges
        WHERE id = %s AND (initiator_id = %s OR recipient_id = %s)
    '''
    exchange = db_manager.fetch_one(query, (exchange_id, user_id, user_id))
    if exchange and exchange['status'] == 'accepted':
        update_query = '''
            UPDATE exchanges
            SET status = %s, completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        '''
        db_manager.execute_query(update_query, ('completed', exchange_id))
        return True
    return False

def submit_rating(exchange_id, rater_id, rated_user_id, rating_value):
    """Submit a rating for a completed exchange"""
    db_manager = DatabaseManager()

    # Validate rating value (1-5)
    if not (1 <= rating_value <= 5):
        return False, "Rating must be between 1 and 5 stars"

    # Check if exchange is completed and user is involved
    exchange_query = '''
        SELECT initiator_id, recipient_id, status
        FROM exchanges
        WHERE id = %s AND status = 'completed'
    '''
    exchange = db_manager.fetch_one(exchange_query, (exchange_id,))

    if not exchange:
        return False, "Exchange not found or not completed"

    # Check if rater is involved in the exchange
    if rater_id not in [exchange['initiator_id'], exchange['recipient_id']]:
        return False, "You are not authorized to rate this exchange"

    # Check if rater is not rating themselves
    if rater_id == rated_user_id:
        return False, "You cannot rate yourself"

    # Check if rating already exists for this exchange and rater
    existing_rating_query = '''
        SELECT id FROM ratings
        WHERE exchange_id = %s AND rater_id = %s
    '''
    existing_rating = db_manager.fetch_one(existing_rating_query, (exchange_id, rater_id))

    if existing_rating:
        return False, "You have already rated this exchange"

    try:
        # Insert the rating
        insert_query = '''
            INSERT INTO ratings (exchange_id, rater_id, rated_user_id, rating)
            VALUES (%s, %s, %s, %s)
        '''
        db_manager.execute_query(insert_query, (exchange_id, rater_id, rated_user_id, rating_value))

        # Update the user's average rating
        update_rating_query = '''
            UPDATE users
            SET rating = (
                SELECT AVG(rating) FROM ratings WHERE rated_user_id = %s
            )
            WHERE id = %s
        '''
        db_manager.execute_query(update_rating_query, (rated_user_id, rated_user_id))

        return True, "Rating submitted successfully"

    except Exception as e:
        return False, f"Error submitting rating: {str(e)}"

def get_user_rating_for_exchange(exchange_id, user_id):
    """Check if user has already rated an exchange"""
    db_manager = DatabaseManager()
    query = '''
        SELECT id FROM ratings
        WHERE exchange_id = %s AND rater_id = %s
    '''
    rating = db_manager.fetch_one(query, (exchange_id, user_id))
    return rating is not None

def get_user_stats(user_id):
    """Get comprehensive stats for a user"""
    db_manager = DatabaseManager()

    # Get skill count
    skill_query = 'SELECT COUNT(*) as skill_count FROM skills WHERE user_id = %s'
    skill_result = db_manager.fetch_one(skill_query, (user_id,))
    skill_count = skill_result['skill_count'] if skill_result else 0

    # Get exchange counts
    exchange_query = '''
        SELECT
            COUNT(*) as total_exchanges,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_exchanges,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_exchanges
        FROM exchanges
        WHERE initiator_id = %s OR recipient_id = %s
    '''
    exchange_result = db_manager.fetch_one(exchange_query, (user_id, user_id))
    total_exchanges = exchange_result['total_exchanges'] if exchange_result and exchange_result['total_exchanges'] is not None else 0
    completed_exchanges = exchange_result['completed_exchanges'] if exchange_result and exchange_result['completed_exchanges'] is not None else 0
    pending_exchanges = exchange_result['pending_exchanges'] if exchange_result and exchange_result['pending_exchanges'] is not None else 0

    # Get skills by category
    category_query = '''
        SELECT category, COUNT(*) as count
        FROM skills
        WHERE user_id = %s
        GROUP BY category
        ORDER BY count DESC
    '''
    skills_by_category = db_manager.fetch_all(category_query, (user_id,))

    # Calculate community points (based on completed exchanges)
    community_points = completed_exchanges * 10  # 10 points per completed exchange

    # Determine badge level
    if community_points >= 100:
        badge = "Gold"
    elif community_points >= 50:
        badge = "Silver"
    elif community_points >= 10:
        badge = "Bronze"
    else:
        badge = "Newcomer"

    return {
        'skill_count': skill_count,
        'total_exchanges': total_exchanges,
        'completed_exchanges': completed_exchanges,
        'pending_exchanges': pending_exchanges,
        'skills_by_category': skills_by_category,
        'community_points': community_points,
        'badge': badge
    }

def get_skills_by_category(user_id):
    """Get skills grouped by category for a user"""
    db_manager = DatabaseManager()
    query = '''
        SELECT category, COUNT(*) as count
        FROM skills
        WHERE user_id = %s
        GROUP BY category
        ORDER BY count DESC
    '''
    return db_manager.fetch_all(query, (user_id,))

def get_recommended_skills(user_id, limit=10):
    """Get recommended skills for a user based on past exchanges and similar users"""
    db_manager = DatabaseManager()

    # Get categories from user's past exchanges
    category_query = '''
        SELECT DISTINCT s.category
        FROM exchanges e
        JOIN skills s ON (e.initiator_skill_id = s.id OR e.recipient_skill_id = s.id)
        WHERE (e.initiator_id = %s OR e.recipient_id = %s) AND e.status = 'completed'
    '''
    user_categories = db_manager.fetch_all(category_query, (user_id, user_id))
    categories = [row['category'] for row in user_categories]

    if not categories:
        # If no past exchanges, recommend popular skills
        popular_query = '''
            SELECT s.id, s.skill_name, s.category, s.proficiency_level, s.description,
                   u.id as user_id, u.full_name, u.email, u.rating,
                   COUNT(*) as popularity
            FROM skills s
            JOIN users u ON s.user_id = u.id
            WHERE s.user_id != %s
            GROUP BY s.id
            ORDER BY popularity DESC, u.rating DESC
            LIMIT %s
        '''
        return db_manager.fetch_all(popular_query, (user_id, limit))

    # Recommend skills from users they've exchanged with, in similar categories
    recommendation_query = '''
        SELECT DISTINCT s.id, s.skill_name, s.category, s.proficiency_level, s.description,
               u.id as user_id, u.full_name, u.email, u.rating
        FROM skills s
        JOIN users u ON s.user_id = u.id
        JOIN exchanges e ON (e.initiator_id = u.id OR e.recipient_id = u.id)
        WHERE s.category IN ({})
          AND s.user_id != %s
          AND (e.initiator_id = %s OR e.recipient_id = %s)
          AND e.status = 'completed'
        ORDER BY u.rating DESC, s.created_at DESC
        LIMIT %s
    '''.format(','.join(['%s'] * len(categories)))

    params = categories + [user_id, user_id, user_id, limit]
    recommendations = db_manager.fetch_all(recommendation_query, params)

    # If not enough recommendations, fill with popular skills in those categories
    if len(recommendations) < limit:
        remaining = limit - len(recommendations)
        popular_query = '''
            SELECT s.id, s.skill_name, s.category, s.proficiency_level, s.description,
                   u.id as user_id, u.full_name, u.email, u.rating
            FROM skills s
            JOIN users u ON s.user_id = u.id
            WHERE s.category IN ({})
              AND s.user_id != %s
              AND s.id NOT IN ({})
            ORDER BY u.rating DESC
            LIMIT %s
        '''.format(','.join(['%s'] * len(categories)),
                   ','.join(['%s'] * len(recommendations)) if recommendations else 'NULL')

        existing_ids = [str(r['id']) for r in recommendations] if recommendations else []
        params = categories + [user_id] + existing_ids + [remaining]
        popular = db_manager.fetch_all(popular_query, params)
        recommendations.extend(popular)

    return recommendations[:limit]

def get_recommended_users(user_id, limit=5):
    """Get recommended users based on similar skills and high ratings"""
    db_manager = DatabaseManager()

    # Get user's skill categories
    user_categories_query = '''
        SELECT DISTINCT category FROM skills WHERE user_id = %s
    '''
    user_categories = db_manager.fetch_all(user_categories_query, (user_id,))
    categories = [row['category'] for row in user_categories]

    if not categories:
        # If user has no skills, recommend top-rated users
        top_users_query = '''
            SELECT id, full_name, email, rating, bio
            FROM users
            WHERE id != %s
            ORDER BY rating DESC, total_exchanges DESC
            LIMIT %s
        '''
        return db_manager.fetch_all(top_users_query, (user_id, limit))

    # Recommend users with skills in similar categories, high ratings
    recommendation_query = '''
        SELECT DISTINCT u.id, u.full_name, u.email, u.rating, u.bio,
               COUNT(s.id) as matching_skills
        FROM users u
        JOIN skills s ON u.id = s.user_id
        WHERE s.category IN ({})
          AND u.id != %s
        GROUP BY u.id
        ORDER BY u.rating DESC, matching_skills DESC
        LIMIT %s
    '''.format(','.join(['%s'] * len(categories)))

    params = categories + [user_id, limit]
    return db_manager.fetch_all(recommendation_query, params)

def create_group_exchange(initiator_id, title, description, max_participants, initiator_skill_id):
    """Create a new group exchange"""
    db_manager = DatabaseManager()
    query = '''
        INSERT INTO exchanges (initiator_id, is_group, title, description, max_participants, initiator_skill_id)
        VALUES (%s, TRUE, %s, %s, %s, %s)
    '''
    db_manager.execute_query(query, (initiator_id, title, description, max_participants, initiator_skill_id))
    return db_manager.fetch_one('SELECT LAST_INSERT_ID() as id')['id']

def add_participant_to_exchange(exchange_id, user_id, skill_id, role='participant'):
    """Add a participant to a group exchange"""
    db_manager = DatabaseManager()
    query = '''
        INSERT INTO exchange_participants (exchange_id, user_id, skill_id, role)
        VALUES (%s, %s, %s, %s)
    '''
    db_manager.execute_query(query, (exchange_id, user_id, skill_id, role))

def get_group_exchange_participants(exchange_id):
    """Get all participants in a group exchange"""
    db_manager = DatabaseManager()
    query = '''
        SELECT ep.id, ep.user_id, ep.skill_id, ep.role, ep.status, ep.joined_at,
               u.full_name, u.email, s.skill_name, s.category
        FROM exchange_participants ep
        JOIN users u ON ep.user_id = u.id
        JOIN skills s ON ep.skill_id = s.id
        WHERE ep.exchange_id = %s
        ORDER BY ep.joined_at ASC
    '''
    return db_manager.fetch_all(query, (exchange_id,))

def accept_group_exchange_participation(participant_id, user_id):
    """Accept participation in a group exchange"""
    db_manager = DatabaseManager()
    query = '''
        UPDATE exchange_participants
        SET status = 'accepted'
        WHERE id = %s AND user_id = %s
    '''
    db_manager.execute_query(query, (participant_id, user_id))

def reject_group_exchange_participation(participant_id, user_id):
    """Reject participation in a group exchange"""
    db_manager = DatabaseManager()
    query = '''
        UPDATE exchange_participants
        SET status = 'rejected'
        WHERE id = %s AND user_id = %s
    '''
    db_manager.execute_query(query, (participant_id, user_id))

def get_user_group_exchanges(user_id):
    """Get all group exchanges for a user"""
    db_manager = DatabaseManager()
    query = '''
        SELECT DISTINCT e.id, e.initiator_id, e.title, e.description, e.status, e.max_participants,
               e.created_at, e.completed_at,
               u.full_name as initiator_name,
               s.skill_name as initiator_skill,
               (COUNT(DISTINCT ep.id) + 1) as current_participants
        FROM exchanges e
        JOIN users u ON e.initiator_id = u.id
        JOIN skills s ON e.initiator_skill_id = s.id
        LEFT JOIN exchange_participants ep ON e.id = ep.exchange_id
        WHERE e.is_group = TRUE AND (e.initiator_id = %s OR ep.user_id = %s)
        GROUP BY e.id
        ORDER BY e.created_at DESC
    '''
    return db_manager.fetch_all(query, (user_id, user_id))

def get_all_available_group_exchanges(user_id):
    """Get all available group exchanges that user can join (excluding their own)"""
    db_manager = DatabaseManager()
    query = '''
        SELECT DISTINCT e.id, e.initiator_id, e.title, e.description, e.status, e.max_participants,
               e.created_at,
               u.full_name as initiator_name,
               s.skill_name as initiator_skill,
               (COUNT(DISTINCT ep.id) + 1) as current_participants,
               EXISTS(
                   SELECT 1 FROM exchange_participants ep2 
                   WHERE ep2.exchange_id = e.id AND ep2.user_id = %s
               ) as user_participating
        FROM exchanges e
        JOIN users u ON e.initiator_id = u.id
        JOIN skills s ON e.initiator_skill_id = s.id
        LEFT JOIN exchange_participants ep ON e.id = ep.exchange_id
        WHERE e.is_group = TRUE 
          AND e.status IN ('pending', 'active')
          AND e.initiator_id != %s
        GROUP BY e.id
        HAVING (COUNT(DISTINCT ep.id) + 1) < e.max_participants OR user_participating = 1
        ORDER BY e.created_at DESC
    '''
    return db_manager.fetch_all(query, (user_id, user_id))

def update_user_profile_picture(user_id, image_base64):
    """Update user's profile picture"""
    db_manager = DatabaseManager()
    query = 'UPDATE users SET profile_image = %s WHERE id = %s'
    db_manager.execute_query(query, (image_base64, user_id))

def update_user_bio(user_id, bio):
    """Update user's bio"""
    db_manager = DatabaseManager()
    query = 'UPDATE users SET bio = %s WHERE id = %s'
    db_manager.execute_query(query, (bio, user_id))

def get_user_profile_extended(user_id):
    """Get extended user profile with all fields"""
    db_manager = DatabaseManager()
    query = '''
        SELECT u.id, u.email, u.full_name, u.bio, u.profile_image, u.rating, 
               u.total_exchanges, u.created_at, COUNT(DISTINCT r.id) as rating_count
        FROM users u
        LEFT JOIN ratings r ON u.id = r.rated_user_id
        WHERE u.id = %s
        GROUP BY u.id
    '''
    return db_manager.fetch_one(query, (user_id,))

def save_message_attachment(exchange_id, sender_id, recipient_id, filename, file_data, file_type):
    """Save a message with file attachment"""
    db_manager = DatabaseManager()
    # Store file info as a structured message with attachment data
    message_text = f"📎 Sent a file: {filename}"
    query = '''
        INSERT INTO messages (sender_id, recipient_id, exchange_id, message, attachment_name, attachment_data, attachment_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    db_manager.execute_query(query, (sender_id, recipient_id, exchange_id, message_text, filename, file_data, file_type))

def get_exchange_analytics(user_id):
    """Get comprehensive analytics for dashboard"""
    db_manager = DatabaseManager()
    
    # Get exchange trends over time
    trends_query = '''
        SELECT 
            DATE_FORMAT(created_at, '%Y-%m') as month,
            COUNT(*) as count,
            status
        FROM exchanges
        WHERE initiator_id = %s OR recipient_id = %s
        GROUP BY month, status
        ORDER BY month
    '''
    trends = db_manager.fetch_all(trends_query, (user_id, user_id))
    
    # Get skill category distribution
    skills_query = '''
        SELECT category, COUNT(*) as count
        FROM skills
        WHERE user_id = %s
        GROUP BY category
    '''
    skills_dist = db_manager.fetch_all(skills_query, (user_id,))
    
    # Get rating distribution
    ratings_query = '''
        SELECT rating, COUNT(*) as count
        FROM ratings
        WHERE rated_user_id = %s
        GROUP BY rating
        ORDER BY rating
    '''
    ratings_dist = db_manager.fetch_all(ratings_query, (user_id,))
    
    return {
        'trends': trends,
        'skills_distribution': skills_dist,
        'ratings_distribution': ratings_dist
    }

def update_social_links(user_id, linkedin=None, github=None, twitter=None, portfolio=None):
    """Update user's social media links"""
    db_manager = DatabaseManager()
    query = '''
        UPDATE users 
        SET linkedin_url = %s, github_url = %s, twitter_url = %s, portfolio_url = %s 
        WHERE id = %s
    '''
    db_manager.execute_query(query, (linkedin, github, twitter, portfolio, user_id))

def get_user_social_links(user_id):
    """Get user's social media links"""
    db_manager = DatabaseManager()
    query = '''
        SELECT linkedin_url, github_url, twitter_url, portfolio_url
        FROM users
        WHERE id = %s
    '''
    return db_manager.fetch_one(query, (user_id,))
