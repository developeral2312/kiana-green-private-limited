import os

# Paths
base_dir = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora"
home_html = os.path.join(base_dir, "templates", "public_view", "home.html")
home_css = os.path.join(base_dir, "static", "css", "public_view", "home.css")
about_html = os.path.join(base_dir, "templates", "public_view", "about.html")
about_css = os.path.join(base_dir, "static", "css", "public_view", "about.css")

html_content = """{% extends 'public_view/base.html' %}

{% block link %}
    <link rel="stylesheet" href="/static/css/public_view/home.css">
    <!-- FontAwesome for Premium Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
{% endblock %}

{% block code %}
<!-- PREMIUM HERO SECTION WITH EMBEDDED FORM -->
<div class="premium-hero position-relative">
    <div class="hero-bg-overlay"></div>
    <div class="container position-relative" style="z-index: 2; padding-top: 60px; padding-bottom: 80px;">
        <div class="row align-items-center">
            
            <!-- Hero Text -->
            <div class="col-lg-7 text-white animate__animated animate__fadeInUp pe-lg-5">
                <div class="premium-badge mb-4">
                    <i class="fa-solid fa-leaf text-success me-2"></i> India's Most Trusted Solar Partner
                </div>
                <h1 class="display-4 fw-bold mb-4" style="line-height: 1.2;">
                    Transform Your Roof Into a <br>
                    <span class="text-gradient-gold">Power Plant.</span>
                </h1>
                <p class="lead mb-5 opacity-75 pe-lg-4" style="font-weight: 300;">
                    Eliminate your electricity bills with Kiana Green's premium solar solutions. From residential rooftops to mega-scale commercial projects, we deliver end-to-end perfection with 25 years of guaranteed performance.
                </p>
                
                <div class="d-flex gap-4 align-items-center flex-wrap mt-2">
                    <div class="d-flex align-items-center">
                        <div class="icon-circle bg-success-subtle text-success me-3"><i class="fa-solid fa-check"></i></div>
                        <div><strong class="d-block">Zero</strong><small class="opacity-75">Maintenance</small></div>
                    </div>
                    <div class="d-flex align-items-center">
                        <div class="icon-circle bg-warning-subtle text-warning me-3"><i class="fa-solid fa-bolt"></i></div>
                        <div><strong class="d-block">100%</strong><small class="opacity-75">Grid Independence</small></div>
                    </div>
                    <div class="d-flex align-items-center">
                        <div class="icon-circle bg-info-subtle text-info me-3"><i class="fa-solid fa-file-signature"></i></div>
                        <div><strong class="d-block">Subsidy</strong><small class="opacity-75">Assistance</small></div>
                    </div>
                </div>
            </div>
            
            <!-- Hero Lead Form -->
            <div class="col-lg-5 mt-5 mt-lg-0 animate__animated animate__fadeInRight">
                <div class="glass-form-card p-4 p-md-5">
                    <div class="text-center mb-4">
                        <h4 class="fw-bold text-dark mb-1">Get Your Free Solar Quote</h4>
                        <p class="text-muted small">Fill out the form below and our experts will contact you within 24 hours.</p>
                    </div>
                    
                    <form action="{% url 'contact' %}" method="POST">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label class="form-label text-dark fw-semibold small">Full Name</label>
                            <input type="text" name="name" class="form-control premium-input" placeholder="e.g. Aditya Sharma" required>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label text-dark fw-semibold small">Phone Number</label>
                                <input type="text" name="phone" class="form-control premium-input" placeholder="+91 XXXXX XXXXX" required>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label text-dark fw-semibold small">Average Monthly Bill</label>
                                <select class="form-select premium-input" name="bill" required>
                                    <option value="">Select Range</option>
                                    <option value="Under ₹3,000">Under ₹3,000</option>
                                    <option value="₹3,000 - ₹5,000">₹3,000 - ₹5,000</option>
                                    <option value="₹5,000 - ₹10,000">₹5,000 - ₹10,000</option>
                                    <option value="Above ₹10,000">Above ₹10,000</option>
                                </select>
                            </div>
                        </div>
                        <div class="mb-4">
                            <label class="form-label text-dark fw-semibold small">City / Location</label>
                            <input type="text" name="location" class="form-control premium-input" placeholder="e.g. Lucknow, UP" required>
                        </div>
                        <button type="submit" class="btn btn-premium-submit w-100 py-3 fw-bold fs-5 shadow">
                            Request Free Consultation <i class="fa-solid fa-arrow-right ms-2"></i>
                        </button>
                        <p class="text-center text-muted mt-3 mb-0" style="font-size: 0.75rem;"><i class="fa-solid fa-lock text-success me-1"></i> Your information is 100% secure.</p>
                    </form>
                </div>
            </div>
            
        </div>
    </div>
</div>

<!-- TRUSTED PARTNERS / BRANDS Ticker -->
<div class="bg-white py-4 border-bottom shadow-sm">
    <div class="container text-center">
        <p class="text-muted small fw-bold text-uppercase tracking-wide mb-3">Premium Technology Partners</p>
        <div class="d-flex justify-content-center align-items-center gap-4 gap-md-5 flex-wrap opacity-50 grayscale-hover">
            <h4 class="fw-bold m-0"><i class="fa-solid fa-sun text-warning me-1"></i> WAAREE</h4>
            <h4 class="fw-bold m-0"><i class="fa-solid fa-charging-station text-primary me-1"></i> ADANI SOLAR</h4>
            <h4 class="fw-bold m-0"><i class="fa-solid fa-bolt text-danger me-1"></i> LUMINOUS</h4>
            <h4 class="fw-bold m-0"><i class="fa-solid fa-plug-circle-bolt text-success me-1"></i> HAVELLS</h4>
            <h4 class="fw-bold m-0"><i class="fa-solid fa-microchip text-dark me-1"></i> GROWATT</h4>
        </div>
    </div>
</div>

<!-- ABOUT OVERVIEW -->
<div class="section-padding bg-light">
    <div class="container">
        <div class="row align-items-center">
            <div class="col-lg-6 mb-5 mb-lg-0">
                <img src="/static/images/energy.avif" class="img-fluid rounded-4 shadow-lg w-100" style="object-fit: cover; height: 500px;">
                <div class="floating-stat-card shadow-lg bg-white p-4 rounded-4 text-center">
                    <h2 class="text-success fw-bolder display-5 mb-0">10+</h2>
                    <p class="text-muted fw-bold mb-0 text-uppercase" style="font-size: 0.8rem; letter-spacing: 1px;">Years of Excellence</p>
                </div>
            </div>
            <div class="col-lg-6 ps-lg-5">
                <h6 class="text-success fw-bold text-uppercase tracking-wider mb-2">About Kiana Green</h6>
                <h2 class="display-6 fw-bold text-dark-navy mb-4">Driving India's Renewable Revolution.</h2>
                <p class="lead text-muted mb-4" style="line-height: 1.8; font-size: 1.1rem;">
                    Kiana Green Private Limited is not just a solar installer; we are your energy partners. We specialize in engineering, procurement, and construction (EPC) of high-efficiency solar power plants tailored to your exact needs.
                </p>
                <div class="row g-4 mt-2">
                    <div class="col-sm-6">
                        <div class="d-flex align-items-start">
                            <i class="fa-solid fa-check-double text-success fs-3 me-3 mt-1"></i>
                            <div>
                                <h5 class="fw-bold mb-1">Tier-1 Modules</h5>
                                <p class="text-muted small">Only the highest grade A+ panels for maximum generation.</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-sm-6">
                        <div class="d-flex align-items-start">
                            <i class="fa-solid fa-file-contract text-success fs-3 me-3 mt-1"></i>
                            <div>
                                <h5 class="fw-bold mb-1">MNRE Subsidy</h5>
                                <p class="text-muted small">Complete paperwork assistance for Govt. subsidies.</p>
                            </div>
                        </div>
                    </div>
                </div>
                <a href="{% url 'about' %}" class="btn btn-outline-dark px-4 py-2 mt-4 rounded-pill fw-bold">Read Full Story</a>
            </div>
        </div>
    </div>
</div>

<!-- WHY CHOOSE US (6 Grid Cards) -->
<div class="section-padding bg-white">
    <div class="container">
        <div class="text-center mb-5 max-w-700 mx-auto">
            <h6 class="text-success fw-bold text-uppercase tracking-wider mb-2">The Advantage</h6>
            <h2 class="display-5 fw-bold text-dark-navy">Why Choose Kiana Green?</h2>
            <p class="text-muted">We combine cutting-edge technology with flawless execution to deliver solar systems that outperform and outlast the competition.</p>
        </div>
        
        <div class="row g-4">
            <div class="col-lg-4 col-md-6">
                <div class="premium-feature-card">
                    <div class="feature-icon bg-blue-light text-primary"><i class="fa-solid fa-hand-holding-dollar"></i></div>
                    <h5 class="fw-bold mt-4 mb-3">Highest ROI</h5>
                    <p class="text-muted mb-0">Our AI-driven site analysis ensures optimal panel placement, guaranteeing the fastest payback period for your investment.</p>
                </div>
            </div>
            <div class="col-lg-4 col-md-6">
                <div class="premium-feature-card">
                    <div class="feature-icon bg-green-light text-success"><i class="fa-solid fa-shield-halved"></i></div>
                    <h5 class="fw-bold mt-4 mb-3">Leak-Proof Civil Work</h5>
                    <p class="text-muted mb-0">Specialized mounting structures and waterproofing techniques ensure zero damage or leakage to your roof.</p>
                </div>
            </div>
            <div class="col-lg-4 col-md-6">
                <div class="premium-feature-card">
                    <div class="feature-icon bg-warning-light text-warning"><i class="fa-solid fa-clock-rotate-left"></i></div>
                    <h5 class="fw-bold mt-4 mb-3">25-Year Warranty</h5>
                    <p class="text-muted mb-0">Peace of mind guaranteed. We offer 25-year performance warranties on panels and 10-year warranties on inverters.</p>
                </div>
            </div>
            <div class="col-lg-4 col-md-6">
                <div class="premium-feature-card">
                    <div class="feature-icon bg-purple-light text-purple"><i class="fa-solid fa-mobile-screen"></i></div>
                    <h5 class="fw-bold mt-4 mb-3">Smart App Monitoring</h5>
                    <p class="text-muted mb-0">Track your daily generation, consumption, and savings in real-time through our advanced mobile application.</p>
                </div>
            </div>
            <div class="col-lg-4 col-md-6">
                <div class="premium-feature-card">
                    <div class="feature-icon bg-danger-light text-danger"><i class="fa-solid fa-file-signature"></i></div>
                    <h5 class="fw-bold mt-4 mb-3">Hassle-Free Approvals</h5>
                    <p class="text-muted mb-0">Net-metering, DISCOM liaisoning, and subsidy claims—we handle 100% of the government paperwork for you.</p>
                </div>
            </div>
            <div class="col-lg-4 col-md-6">
                <div class="premium-feature-card">
                    <div class="feature-icon bg-dark-light text-dark"><i class="fa-solid fa-headset"></i></div>
                    <h5 class="fw-bold mt-4 mb-3">24/7 Dedicated Support</h5>
                    <p class="text-muted mb-0">Our rapid-response O&M team ensures your plant never stops generating. Free maintenance for the first year.</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- HOW IT WORKS (Process Steps) -->
<div class="section-padding bg-dark-navy text-white">
    <div class="container text-center">
        <h6 class="text-success fw-bold text-uppercase tracking-wider mb-2">Our Process</h6>
        <h2 class="display-5 fw-bold mb-5">From Concept to Commissioning</h2>
        
        <div class="row g-4 position-relative z-1">
            <!-- Connecting line for desktop -->
            <div class="process-line d-none d-lg-block"></div>
            
            <div class="col-lg-3 col-md-6">
                <div class="process-card">
                    <div class="process-number">1</div>
                    <h5 class="fw-bold mt-4 mb-3 text-white">Site Survey</h5>
                    <p class="text-light opacity-75 small">Our engineers visit your site to analyze shadow-free area, roof strength, and electrical load.</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="process-card">
                    <div class="process-number bg-primary">2</div>
                    <h5 class="fw-bold mt-4 mb-3 text-white">3D Design & Proposal</h5>
                    <p class="text-light opacity-75 small">We provide a custom 3D layout of the plant along with a detailed ROI and payback financial model.</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="process-card">
                    <div class="process-number bg-warning">3</div>
                    <h5 class="fw-bold mt-4 mb-3 text-white">Execution & Setup</h5>
                    <p class="text-light opacity-75 small">Swift, clean, and safe installation by certified technicians using premium Tier-1 equipment.</p>
                </div>
            </div>
            <div class="col-lg-3 col-md-6">
                <div class="process-card">
                    <div class="process-number bg-success">4</div>
                    <h5 class="fw-bold mt-4 mb-3 text-white">Net Metering</h5>
                    <p class="text-light opacity-75 small">We complete the grid synchronization, activate net-metering, and hand over the live monitoring app.</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- SERVICES SECTION -->
<div class="section-padding bg-light" id="services">
    <div class="container">
        <div class="text-center mb-5">
            <h6 class="text-success fw-bold text-uppercase tracking-wider mb-2">Solutions</h6>
            <h2 class="display-5 fw-bold text-dark-navy">Solar For Every Need</h2>
        </div>
        <div class="row g-4">
            <div class="col-lg-4">
                <div class="service-card-premium border-0 shadow-sm rounded-4 overflow-hidden bg-white h-100">
                    <img src="/static/images/home.png" class="w-100" style="height: 240px; object-fit: cover;">
                    <div class="p-4">
                        <span class="badge bg-success-subtle text-success mb-3 px-3 py-2">Residential</span>
                        <h4 class="fw-bold text-dark mb-3">Home Solar Systems</h4>
                        <p class="text-muted mb-4">Transform your home into a green powerhouse. Slash your electricity bills to zero and enjoy government subsidies.</p>
                        <ul class="list-unstyled text-muted small mb-0">
                            <li class="mb-2"><i class="fa-solid fa-check text-success me-2"></i> On-Grid & Hybrid Options</li>
                            <li class="mb-2"><i class="fa-solid fa-check text-success me-2"></i> Subsidy Processing</li>
                            <li><i class="fa-solid fa-check text-success me-2"></i> Battery Backup Integration</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="service-card-premium border-0 shadow-sm rounded-4 overflow-hidden bg-white h-100">
                    <img src="/static/images/com.png" class="w-100" style="height: 240px; object-fit: cover;">
                    <div class="p-4">
                        <span class="badge bg-primary-subtle text-primary mb-3 px-3 py-2">Commercial</span>
                        <h4 class="fw-bold text-dark mb-3">Industrial Solar Plants</h4>
                        <p class="text-muted mb-4">Reduce operational costs and claim accelerated depreciation. Heavy-duty plants engineered for high energy yields.</p>
                        <ul class="list-unstyled text-muted small mb-0">
                            <li class="mb-2"><i class="fa-solid fa-check text-success me-2"></i> OPEX & CAPEX Models</li>
                            <li class="mb-2"><i class="fa-solid fa-check text-success me-2"></i> Accelerated Depreciation</li>
                            <li><i class="fa-solid fa-check text-success me-2"></i> Heavy-Duty Structures</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="service-card-premium border-0 shadow-sm rounded-4 overflow-hidden bg-white h-100">
                    <img src="/static/images/service.jpg" class="w-100" style="height: 240px; object-fit: cover;">
                    <div class="p-4">
                        <span class="badge bg-warning-subtle text-warning mb-3 px-3 py-2">Maintenance</span>
                        <h4 class="fw-bold text-dark mb-3">Solar O&M Services</h4>
                        <p class="text-muted mb-4">Ensure your plant operates at 100% efficiency year-round. We provide deep cleaning and technical auditing.</p>
                        <ul class="list-unstyled text-muted small mb-0">
                            <li class="mb-2"><i class="fa-solid fa-check text-success me-2"></i> Robotic & Manual Cleaning</li>
                            <li class="mb-2"><i class="fa-solid fa-check text-success me-2"></i> Inverter Health Checks</li>
                            <li><i class="fa-solid fa-check text-success me-2"></i> AMC Contracts</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- DYNAMIC PROJECTS -->
<div class="section-padding bg-white" id="projects">
    <div class="container">
        <div class="d-flex justify-content-between align-items-end mb-5">
            <div>
                <h6 class="text-success fw-bold text-uppercase tracking-wider mb-2">Portfolio</h6>
                <h2 class="display-5 fw-bold text-dark-navy m-0">Recent Installations</h2>
            </div>
            <a href="{% url 'projects' %}" class="btn btn-outline-dark rounded-pill px-4 d-none d-md-block">View All Gallery</a>
        </div>
        
        <div class="row g-4">
            {% for item in project_data %}
            <div class="col-md-4">
                <div class="card project-card-premium h-100 border-0 shadow-sm rounded-4 overflow-hidden">
                    {% if item.photo %}
                        <div class="project-img-wrapper position-relative">
                            <img src="{{ item.photo.file.url }}" class="w-100" style="height: 280px; object-fit: cover;">
                            <div class="project-overlay text-white p-3 d-flex flex-column justify-content-end">
                                <span class="badge bg-success mb-2 align-self-start">{{ item.project.get_project_type_display }}</span>
                                <h5 class="fw-bold mb-1">{{ item.project.feasibility.suggested_capacity|floatformat:0 }}kW Power Plant</h5>
                                <p class="small m-0"><i class="fa-solid fa-location-dot text-warning me-1"></i> {{item.project.location}}</p>
                            </div>
                        </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>

<!-- DYNAMIC REVIEWS & TESTIMONIALS -->
<div class="section-padding bg-light">
    <div class="container">
        <div class="text-center mb-5">
            <h6 class="text-success fw-bold text-uppercase tracking-wider mb-2">Testimonials</h6>
            <h2 class="display-5 fw-bold text-dark-navy">Customer Stories</h2>
        </div>
        
        <div class="row g-4 mb-5">
            {% for review in reviews %}
            <div class="col-md-4">
                <div class="review-card-modern bg-white p-4 rounded-4 shadow-sm border-0 h-100 position-relative">
                    <i class="fa-solid fa-quote-right position-absolute top-0 end-0 mt-4 me-4 text-light" style="font-size: 3rem;"></i>
                    <div class="text-warning mb-3 fs-5">
                        {% for i in "12345"|make_list %}
                            {% if forloop.counter <= review.rating %}
                                <i class="fa-solid fa-star"></i>
                            {% else %}
                                <i class="fa-regular fa-star"></i>
                            {% endif %}
                        {% endfor %}
                    </div>
                    <p class="text-muted fst-italic mb-4" style="line-height: 1.7; position: relative; z-index: 2;">"{{ review.review_text }}"</p>
                    <div class="d-flex align-items-center mt-auto">
                        <div class="avatar-circle bg-dark-navy text-white fw-bold d-flex align-items-center justify-content-center rounded-circle me-3" style="width: 50px; height: 50px; font-size: 1.2rem;">
                            {{ review.name|make_list|first|upper }}
                        </div>
                        <div>
                            <h6 class="fw-bold text-dark mb-0">{{ review.name }}</h6>
                            <small class="text-success"><i class="fa-solid fa-location-dot me-1"></i> {{ review.location|default:"Customer" }}</small>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="text-center">
            <button class="btn btn-success rounded-pill px-5 py-3 fw-bold shadow" data-bs-toggle="modal" data-bs-target="#reviewModal">
                <i class="fa-solid fa-pen-nib me-2"></i> Share Your Experience
            </button>
        </div>
    </div>
</div>

<!-- FOOTER CTA -->
<div class="cta-banner position-relative py-5">
    <div class="container py-5 text-center text-white position-relative" style="z-index: 2;">
        <h2 class="display-4 fw-bold mb-4">Stop Paying For Electricity.</h2>
        <p class="lead mb-5 opacity-75 max-w-700 mx-auto">Take control of your energy bills today. Connect with our solar experts for a free, no-obligation site survey and ROI calculation.</p>
        <a href="{% url 'contact' %}" class="btn btn-warning btn-lg px-5 py-3 rounded-pill fw-bold shadow-lg">
            Get Your Free Quote <i class="fa-solid fa-arrow-right ms-2"></i>
        </a>
    </div>
</div>

<!-- Review Modal (Unchanged Backend Logic) -->
<div class="modal fade" id="reviewModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg rounded-4">
            <div class="modal-header bg-dark-navy text-white border-0 rounded-top-4">
                <h5 class="modal-title fw-bold">Submit a Review</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body p-4 bg-light">
                <form method="POST" class="bg-white p-4 rounded-3 shadow-sm border">
                    {% csrf_token %}
                    {{ form.as_p }}
                    
                    <div class="mb-3">
                        <label class="form-label fw-semibold text-dark">Rating</label>
                        <div class="d-flex gap-2 text-warning fs-4 star-rating" style="cursor: pointer;">
                            <i class="fa-regular fa-star" data-val="1"></i>
                            <i class="fa-regular fa-star" data-val="2"></i>
                            <i class="fa-regular fa-star" data-val="3"></i>
                            <i class="fa-regular fa-star" data-val="4"></i>
                            <i class="fa-regular fa-star" data-val="5"></i>
                        </div>
                        <input type="hidden" name="rating" id="ratingInput" required>
                    </div>
                    
                    <button type="submit" class="btn btn-success w-100 fw-bold py-3 mt-3 rounded-pill shadow-sm">Submit Review</button>
                </form>
            </div>
        </div>
    </div>
</div>

<script>
    document.addEventListener("DOMContentLoaded", function() {
        const stars = document.querySelectorAll(".star-rating i");
        const ratingInput = document.getElementById("ratingInput");

        stars.forEach(star => {
            star.addEventListener("click", function() {
                let rating = this.getAttribute("data-val");
                ratingInput.value = rating;
                stars.forEach(s => {
                    s.classList.remove("fa-solid");
                    s.classList.add("fa-regular");
                });
                for (let i = 0; i < rating; i++) {
                    stars[i].classList.remove("fa-regular");
                    stars[i].classList.add("fa-solid");
                }
            });
        });
    });
</script>
{% endblock %}
"""

css_content = """/* ULTRA PREMIUM HOME CSS */

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

body {
    font-family: 'Outfit', sans-serif;
    color: #4b5563;
    background-color: #f8fafc;
}

.text-dark-navy { color: #0f172a !important; }
.text-gradient-gold {
    background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.bg-dark-navy { background-color: #0f172a !important; }
.tracking-wider { letter-spacing: 0.1em; }
.section-padding { padding: 100px 0; }
.max-w-700 { max-width: 700px; }

/* Form Resets for Premium Look */
input.premium-input, select.premium-input, textarea.premium-input {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 16px;
    background: #f8fafc;
    transition: all 0.3s;
}
input.premium-input:focus, select.premium-input:focus {
    border-color: #22c55e;
    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.1);
    background: white;
}

/* =======================
   HERO SECTION
======================= */
.premium-hero {
    min-height: 95vh;
    background: url('/static/images/hero.png') no-repeat center center/cover;
    background-attachment: fixed;
    display: flex;
    align-items: center;
}
.hero-bg-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.7) 100%);
    z-index: 1;
}
.premium-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 8px 20px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.icon-circle {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
}
.bg-success-subtle { background-color: #dcfce7 !important; color: #16a34a !important; }
.bg-warning-subtle { background-color: #fef3c7 !important; color: #d97706 !important; }
.bg-info-subtle { background-color: #e0f2fe !important; color: #0284c7 !important; }
.bg-primary-subtle { background-color: #dbeafe !important; color: #2563eb !important; }

/* Lead Form Glass */
.glass-form-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255,255,255,0.4);
}
.btn-premium-submit {
    background: linear-gradient(to right, #16a34a, #15803d);
    color: white;
    border: none;
    border-radius: 12px;
    transition: transform 0.3s, box-shadow 0.3s;
}
.btn-premium-submit:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(22, 163, 74, 0.4);
    color: white;
}

/* =======================
   TRUSTED TICKER
======================= */
.grayscale-hover h4 {
    transition: all 0.3s;
    filter: grayscale(100%);
    opacity: 0.6;
}
.grayscale-hover h4:hover {
    filter: grayscale(0%);
    opacity: 1;
}

/* =======================
   ABOUT OVERVIEW
======================= */
.floating-stat-card {
    position: absolute;
    bottom: -30px;
    right: -30px;
    border: 1px solid rgba(0,0,0,0.05);
}

/* =======================
   WHY CHOOSE US
======================= */
.premium-feature-card {
    background: white;
    padding: 40px 30px;
    border-radius: 20px;
    height: 100%;
    transition: all 0.3s ease;
    border: 1px solid #f1f5f9;
}
.premium-feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1);
    border-color: #e2e8f0;
}
.feature-icon {
    width: 65px;
    height: 65px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.8rem;
}
.bg-blue-light { background: #eff6ff; }
.bg-green-light { background: #f0fdf4; }
.bg-warning-light { background: #fffbeb; }
.bg-purple-light { background: #faf5ff; color: #9333ea; }
.bg-danger-light { background: #fef2f2; }
.bg-dark-light { background: #f8fafc; }

/* =======================
   PROCESS
======================= */
.process-card {
    position: relative;
    padding: 30px 20px;
    background: rgba(255,255,255,0.03);
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.05);
    height: 100%;
    transition: all 0.3s;
}
.process-card:hover {
    background: rgba(255,255,255,0.08);
    transform: translateY(-5px);
}
.process-number {
    width: 50px;
    height: 50px;
    background: #475569;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0 auto;
    position: relative;
    z-index: 2;
    border: 4px solid #0f172a;
}
.process-line {
    position: absolute;
    top: 55px;
    left: 10%;
    right: 10%;
    height: 2px;
    background: dashed 2px rgba(255,255,255,0.2);
    z-index: 0;
}

/* =======================
   SERVICES & PROJECTS
======================= */
.service-card-premium {
    transition: all 0.4s ease;
}
.service-card-premium:hover {
    transform: translateY(-10px);
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15) !important;
}
.project-card-premium {
    transition: all 0.4s ease;
}
.project-card-premium:hover {
    transform: scale(1.03);
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.2) !important;
}
.project-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(15, 23, 42, 0.9) 0%, transparent 100%);
    opacity: 0;
    transition: opacity 0.3s;
}
.project-card-premium:hover .project-overlay {
    opacity: 1;
}

/* =======================
   REVIEWS
======================= */
.review-card-modern {
    transition: all 0.3s ease;
}
.review-card-modern:hover {
    box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1) !important;
    transform: translateY(-5px);
}

/* =======================
   CTA BANNER
======================= */
.cta-banner {
    background: url('/static/images/energy.avif') no-repeat center center/cover;
    background-attachment: fixed;
}
.cta-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(15, 23, 42, 0.85);
    z-index: 1;
}

@media (max-width: 991px) {
    .floating-stat-card {
        right: 20px;
        bottom: -20px;
    }
}
"""


about_html_content = """{% extends 'public_view/base.html' %}

{% block link %}
    <link rel="stylesheet" href="/static/css/public_view/about.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
{% endblock %}

{% block code %}
<!-- About Hero -->
<div class="about-hero position-relative d-flex align-items-center justify-content-center text-center">
    <div class="hero-overlay"></div>
    <div class="container position-relative z-2">
        <h1 class="display-3 fw-bold text-white mb-3">About Kiana Green</h1>
        <p class="lead text-white opacity-75 max-w-700 mx-auto">We are on a mission to accelerate India's transition to sustainable and reliable solar energy.</p>
    </div>
</div>

<div class="container py-5 my-5">
    <div class="row align-items-center">
        <div class="col-lg-6 mb-5 mb-lg-0 pe-lg-5">
            <h6 class="text-success fw-bold text-uppercase tracking-wider mb-2">Our Story</h6>
            <h2 class="display-5 fw-bold text-dark-navy mb-4">Building a Greener Tomorrow, Today.</h2>
            <p class="text-muted lead mb-4" style="line-height: 1.8;">
                Established with a vision to make solar energy accessible and reliable, Kiana Green Private Limited has grown into one of the most trusted EPC (Engineering, Procurement, and Construction) companies in the renewable sector.
            </p>
            <p class="text-muted mb-4" style="line-height: 1.8;">
                Unlike traditional installers, we take a holistic engineering approach. From shadow analysis using advanced 3D software to selecting the absolute best Tier-1 components for your specific microclimate, we ensure your plant generates maximum yield for the next 25 years.
            </p>
            
            <div class="row g-4 mt-2">
                <div class="col-6">
                    <h2 class="fw-bold text-success display-5 mb-0">500+</h2>
                    <p class="text-muted fw-bold text-uppercase small">Installations</p>
                </div>
                <div class="col-6">
                    <h2 class="fw-bold text-success display-5 mb-0">15 MW+</h2>
                    <p class="text-muted fw-bold text-uppercase small">Total Capacity</p>
                </div>
            </div>
        </div>
        <div class="col-lg-6">
            <div class="row g-3">
                <div class="col-6">
                    <img src="/static/images/expert.png" class="img-fluid rounded-4 shadow-sm w-100 mb-3" style="height: 250px; object-fit: cover;">
                    <img src="/static/images/save.jpg" class="img-fluid rounded-4 shadow-sm w-100" style="height: 300px; object-fit: cover;">
                </div>
                <div class="col-6 mt-5">
                    <img src="/static/images/hero.png" class="img-fluid rounded-4 shadow-sm w-100 mb-3" style="height: 300px; object-fit: cover;">
                    <img src="/static/images/energy.avif" class="img-fluid rounded-4 shadow-sm w-100" style="height: 250px; object-fit: cover;">
                </div>
            </div>
        </div>
    </div>
</div>

<div class="bg-light py-5">
    <div class="container py-5 text-center">
        <h2 class="display-5 fw-bold text-dark-navy mb-5">Our Core Values</h2>
        <div class="row g-4">
            <div class="col-md-4">
                <div class="bg-white p-5 rounded-4 shadow-sm h-100">
                    <i class="fa-solid fa-gem text-success display-4 mb-4"></i>
                    <h4 class="fw-bold mb-3">Uncompromising Quality</h4>
                    <p class="text-muted">We never cut corners. From Tier-1 panels to heavy-duty galvanized structures, quality is engineered into every project.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="bg-white p-5 rounded-4 shadow-sm h-100">
                    <i class="fa-solid fa-handshake-angle text-primary display-4 mb-4"></i>
                    <h4 class="fw-bold mb-3">Customer Transparency</h4>
                    <p class="text-muted">No hidden costs. No false generation promises. We provide realistic ROI models and stick to our timelines.</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="bg-white p-5 rounded-4 shadow-sm h-100">
                    <i class="fa-solid fa-leaf text-warning display-4 mb-4"></i>
                    <h4 class="fw-bold mb-3">Sustainability First</h4>
                    <p class="text-muted">Our goal isn't just business; it's maximizing carbon offset and creating a truly sustainable energy grid.</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

about_css_content = """/* ABOUT CSS */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

body {
    font-family: 'Outfit', sans-serif;
}
.text-dark-navy { color: #0f172a !important; }
.tracking-wider { letter-spacing: 0.1em; }
.max-w-700 { max-width: 700px; }

.about-hero {
    min-height: 50vh;
    background: url('/static/images/energy.avif') no-repeat center center/cover;
    background-attachment: fixed;
}
.hero-overlay {
    position: absolute;
    inset: 0;
    background: rgba(15, 23, 42, 0.85);
    z-index: 1;
}
"""

with open(home_html, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(home_css, "w", encoding="utf-8") as f:
    f.write(css_content)
    
with open(about_html, "w", encoding="utf-8") as f:
    f.write(about_html_content)
    
with open(about_css, "w", encoding="utf-8") as f:
    f.write(about_css_content)

print("Super advanced design applied.")
