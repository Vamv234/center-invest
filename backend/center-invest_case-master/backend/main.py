"""
Образовательный симулятор защиты личных данных
Educational Data Protection Simulator - Backend API
"""

from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

from database import engine, Base, get_db
from models import User, AttackScenario, UserProgress, UserCertificate
import schemas
from auth import create_access_token, get_current_user, hash_password, verify_password

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Data Protection Simulator API",
    description="Educational simulator for learning cybersecurity threats",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Exception Handlers ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# ============ Authentication Routes ============

@app.post("/api/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user with validation"""
    try:
        # Check if email exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            logger.warning(f"Registration attempt with existing email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check username availability
        existing_username = db.query(User).filter(User.username == user.username).first()
        if existing_username:
            logger.warning(f"Registration attempt with existing username: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        new_user = User(
            email=user.email,
            username=user.username,
            password_hash=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate token
        access_token = create_access_token(data={"sub": new_user.id})
        
        logger.info(f"✓ User registered: {user.email}")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed: " + str(e)
        )


@app.post("/api/auth/login", response_model=schemas.UserResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user with credentials"""
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        
        if not db_user or not verify_password(user.password, db_user.password_hash):
            logger.warning(f"Failed login attempt for: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        access_token = create_access_token(data={"sub": db_user.id})
        
        logger.info(f"✓ User logged in: {user.email}")
        
        return {
            "id": db_user.id,
            "email": db_user.email,
            "username": db_user.username,
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }


# ============ Scenario Routes ============

@app.get("/api/scenarios", response_model=list[schemas.AttackScenarioResponse])
def get_scenarios(
    difficulty: str = Query(None, regex="^(beginner|intermediate|advanced)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all attack scenarios (requires authentication)"""
    try:
        query = db.query(AttackScenario)
        if difficulty:
            query = query.filter(AttackScenario.difficulty == difficulty)
        scenarios = query.all()
        logger.info(f"User {current_user.email} fetched {len(scenarios)} scenarios")
        return scenarios
    except Exception as e:
        logger.error(f"Error fetching scenarios: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scenarios"
        )


@app.get("/api/scenarios/{scenario_id}", response_model=schemas.AttackScenarioDetailResponse)
def get_scenario(
    scenario_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific scenario with all choices (requires authentication)"""
    try:
        scenario = db.query(AttackScenario).filter(AttackScenario.id == scenario_id).first()
        if not scenario:
            logger.warning(f"Scenario not found: {scenario_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found"
            )
        logger.info(f"User {current_user.email} fetched scenario {scenario_id}")
        return scenario
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching scenario: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch scenario"
        )


# ============ Game Progress Routes ============

@app.post("/api/progress/start", response_model=schemas.UserProgressResponse)
def start_scenario(
    payload: schemas.StartScenarioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new scenario"""
    try:
        scenario = db.query(AttackScenario).filter(
            AttackScenario.id == payload.scenario_id
        ).first()
        if not scenario:
            logger.warning(f"Scenario not found: {payload.scenario_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found"
            )
        
        # Check if user already has active progress
        existing = db.query(UserProgress).filter(
            (UserProgress.user_id == current_user.id) &
            (UserProgress.scenario_id == payload.scenario_id) &
            (UserProgress.status == "in_progress")
        ).first()
        
        if existing:
            logger.info(f"User {current_user.email} continuing scenario {payload.scenario_id}")
            return existing
        
        progress = UserProgress(
            user_id=current_user.id,
            scenario_id=payload.scenario_id,
            started_at=datetime.utcnow(),
            security_level=100,
            status="in_progress",
            correct_choices=0,
            total_choices=0
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        
        logger.info(f"User {current_user.email} started scenario {payload.scenario_id}")
        return progress
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting scenario: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start scenario"
        )


@app.post("/api/progress/{progress_id}/choice", response_model=schemas.ChoiceResultResponse)
def submit_choice(
    progress_id: int,
    choice: schemas.ChoiceSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a choice in the scenario"""
    try:
        progress = db.query(UserProgress).filter(
            (UserProgress.id == progress_id) &
            (UserProgress.user_id == current_user.id)
        ).first()
        
        if not progress:
            logger.warning(f"Progress not found: {progress_id} for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress not found"
            )
        
        if progress.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scenario already completed"
            )
        
        scenario = progress.scenario
        if not scenario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scenario not found"
            )
        
        # Safely find the correct choice
        is_correct = False
        consequence = "Choice recorded"
        
        if hasattr(scenario, 'attack_steps') and scenario.attack_steps:
            for step in scenario.attack_steps:
                if step.get("id") == choice.step_id:
                    for option in step.get("choices", []):
                        if option.get("id") == choice.choice_id:
                            is_correct = option.get("is_safe", False)
                            consequence = option.get("consequence", "Choice recorded")
                            break
                    break
        
        # Update progress
        if is_correct:
            progress.security_level = min(100, progress.security_level + 10)
            progress.correct_choices += 1
        else:
            progress.security_level = max(0, progress.security_level - 20)
        
        progress.total_choices += 1
        
        # Mark as completed if final
        if choice.is_final:
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
            
            # Award certificate if perfect score
            if progress.security_level == 100:
                existing_cert = db.query(UserCertificate).filter(
                    (UserCertificate.user_id == current_user.id) &
                    (UserCertificate.scenario_id == scenario.id)
                ).first()
                
                if not existing_cert:
                    cert = UserCertificate(
                        user_id=current_user.id,
                        scenario_id=scenario.id,
                        achievement="perfect_score",
                        created_at=datetime.utcnow()
                    )
                    db.add(cert)
                    logger.info(f"✓ Certificate awarded to user {current_user.email} for scenario {scenario.id}")
        
        db.commit()
        db.refresh(progress)
        
        accuracy = (progress.correct_choices / progress.total_choices * 100) if progress.total_choices > 0 else 0
        
        logger.info(f"Choice submitted - User: {current_user.email}, Scenario: {scenario.id}, Correct: {is_correct}")
        
        return {
            "is_correct": is_correct,
            "explanation": consequence,
            "security_level": progress.security_level,
            "total_choices": progress.total_choices,
            "correct_choices": progress.correct_choices,
            "accuracy": accuracy
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting choice: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit choice"
        )


@app.get("/api/user/progress", response_model=list[schemas.UserProgressResponse])
def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress across all scenarios"""
    try:
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id
        ).all()
        logger.info(f"Fetched progress for user {current_user.email}: {len(progress)} entries")
        return progress
    except Exception as e:
        logger.error(f"Error fetching user progress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch progress"
        )


@app.get("/api/user/stats", response_model=schemas.UserStatsResponse)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    try:
        progresses = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id
        ).all()
        
        completed = [p for p in progresses if p.status == "completed"]
        total_correct = sum(p.correct_choices for p in progresses)
        total_choices = sum(p.total_choices for p in progresses)
        
        certificates = db.query(UserCertificate).filter(
            UserCertificate.user_id == current_user.id
        ).count()
        
        avg_security = sum(p.security_level for p in completed) / len(completed) if completed else 0
        accuracy = (total_correct / total_choices * 100) if total_choices > 0 else 0
        
        # Determine user rank based on achievements
        if len(completed) >= 5 and avg_security >= 90:
            rank = "Expert"
        elif len(completed) >= 3 and avg_security >= 80:
            rank = "Advanced"
        elif len(completed) >= 1:
            rank = "Intermediate"
        else:
            rank = "Beginner"
        
        logger.info(f"Fetched stats for user {current_user.email}: {len(completed)} completed scenarios")
        
        return {
            "total_scenarios_completed": len(completed),
            "total_scenarios_attempted": len(progresses),
            "average_security_level": round(avg_security, 2),
            "total_correct_choices": total_correct,
            "total_choices": total_choices,
            "accuracy": round(accuracy, 2),
            "certificates_earned": certificates,
            "rank": rank
        }
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stats"
        )


@app.get("/api/user/certificates", response_model=list[schemas.CertificateResponse])
def get_user_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's certificates"""
    try:
        certificates = db.query(UserCertificate).filter(
            UserCertificate.user_id == current_user.id
        ).all()
        logger.info(f"Fetched {len(certificates)} certificates for user {current_user.email}")
        return certificates
    except Exception as e:
        logger.error(f"Error fetching certificates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch certificates"
        )


@app.get("/api/certificates/{certificate_id}", response_model=dict)
def get_certificate_details(
    certificate_id: int,
    db: Session = Depends(get_db)
):
    """Get certificate details for verification (public endpoint - no auth required)"""
    try:
        certificate = db.query(UserCertificate).filter(
            UserCertificate.id == certificate_id
        ).first()
        
        if not certificate:
            logger.warning(f"Certificate {certificate_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Certificate not found"
            )
        
        # Get user and scenario details
        user = db.query(User).filter(User.id == certificate.user_id).first()
        scenario = db.query(AttackScenario).filter(AttackScenario.id == certificate.scenario_id).first()
        
        logger.info(f"Certificate {certificate_id} verified for user {user.email if user else 'unknown'}")
        
        return {
            "id": certificate.id,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            } if user else None,
            "scenario": {
                "id": scenario.id,
                "title": scenario.title,
                "description": scenario.description,
                "attack_type": scenario.attack_type,
                "difficulty": scenario.difficulty
            } if scenario else None,
            "achievement": certificate.achievement,
            "created_at": certificate.created_at,
            "verified": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching certificate details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch certificate details"
        )


# ============ Health Check ============

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "data-protection-simulator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
