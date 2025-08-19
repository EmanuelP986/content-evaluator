import streamlit as st
import openai
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define the evaluation prompt
EVALUATION_PROMPT = """You are an expert SEO content evaluator.  
Your task is to rigorously evaluate web content using the **entirety** of both:  
- Google Helpful Content Guidelines  
- Google Search Quality Evaluator Guidelines  

GOOGLE HELPFUL CONTENT GUIDELINES (Use these exact criteria):

Google's automated ranking systems are designed to present helpful, reliable information that's primarily created to benefit people, not to gain search engine rankings.

Content and quality questions:
• Does the content provide original information, reporting, research, or analysis?
• Does the content provide a substantial, complete, or comprehensive description of the topic?
• Does the content provide insightful analysis or interesting information that is beyond the obvious?
• If the content draws on other sources, does it avoid simply copying or rewriting those sources, and instead provide substantial additional value and originality?
• Does the main heading or page title provide a descriptive, helpful summary of the content?
• Does the main heading or page title avoid exaggerating or being shocking in nature?
• Is this the sort of page you'd want to bookmark, share with a friend, or recommend?
• Would you expect to see this content in or referenced by a printed magazine, encyclopedia, or book?
• Does the content provide substantial value when compared to other pages in search results?
• Does the content have any spelling or stylistic issues?
• Is the content produced well, or does it appear sloppy or hastily produced?
• Is the content mass-produced by or outsourced to a large number of creators, or spread across a large network of sites, so that individual pages or sites don't get as much attention or care?

Expertise questions:
• Does the content present information in a way that makes you want to trust it, such as clear sourcing, evidence of the expertise involved, background about the author or the site that publishes it, such as through links to an author page or a site's About page?
• If someone researched the site producing the content, would they come away with an impression that it is well-trusted or widely-recognized as an authority on its topic?
• Is this content written or reviewed by an expert or enthusiast who demonstrably knows the topic well?
• Does the content have any easily-verified factual errors?

People-first content questions:
• Do you have an existing or intended audience for your business or site that would find the content useful if they came directly to you?
• Does your content clearly demonstrate first-hand expertise and a depth of knowledge (for example, expertise that comes from having actually used a product or service, or visiting a place)?
• Does your site have a primary purpose or focus?
• After reading your content, will someone leave feeling they've learned enough about a topic to help achieve their goal?
• Will someone reading your content leave feeling like they've had a satisfying experience?

E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness):
• Trust is most important - the others contribute to trust
• Content doesn't necessarily have to demonstrate all aspects
• Higher standards for YMYL (Your Money or Your Life) topics affecting health, financial stability, safety

"Who, How, and Why" evaluation:
GOOGLE SEARCH QUALITY RATER GUIDELINES (Use these exact criteria):

Google works with ~16,000 external Search Quality Raters globally who evaluate search results using the complete 181-page official guidelines. Use these comprehensive evaluation criteria:

## Page Quality (PQ) Rating Process - How well the page achieves its purpose:

**Step 1: Determine the purpose of the page**
Common helpful purposes include:
• Share information about a topic
• Share personal experience, perspective, or feelings
• Share pictures, videos, or other media
• Demonstrate personal talent or skill
• Express opinion or point of view
• Entertain
• Offer products or services
• Allow people to post questions for others to answer
• Allow people to share files or download software

**Step 2: Assess if page is harmful or has harmful purpose**
Pages with harmful purpose or potential to cause harm = Lowest rating immediately
• Harmful to Self or Other Individuals: encourages/depicts/incites physical, mental, emotional, financial harm
• Harmful to Specified Groups: promotes/condones/incites hatred against groups based on age, caste, disability, ethnicity, gender identity, immigration status, nationality, race, religion, sex/gender, sexual orientation, veteran status, victims of violence, or other marginalized characteristics
• Harmfully Misleading Information: misleads in ways that could cause harm (clearly inaccurate harmful info, claims contradicting expert consensus, unsubstantiated theories not grounded in evidence)

**Step 3: Determine PQ rating (Lowest to Highest scale):**
• **HIGHEST**: Serves beneficial purpose, achieves purpose very well. Very high quality MC with very high effort/originality/talent/skill. Very positive reputation. Very high E-E-A-T
• **HIGH**: Serves beneficial purpose, achieves purpose well. High quality MC with high effort/originality/talent/skill. Positive reputation. High E-E-A-T  
• **MEDIUM**: Has beneficial purpose and achieves it, but doesn't merit High rating OR has strong High characteristics but also mild Low characteristics
• **LOW**: Intended to serve beneficial purpose but doesn't achieve it well due to lacking important dimension. Inadequate E-E-A-T, low quality MC, mildly negative reputation, unsatisfying website information
• **LOWEST**: Untrustworthy, deceptive, harmful to people/society, or other highly undesirable characteristics

**Main Content (MC) Quality Assessment:**
High quality MC requires:
• **Effort**: Significant human work to create satisfying content
• **Originality**: Unique content not available elsewhere, or original source
• **Talent/Skill**: Created with enough talent/skill for satisfying experience
• **Accuracy**: Factually accurate, consistent with expert consensus for YMYL topics

**E-E-A-T Assessment (Experience, Expertise, Authoritativeness, Trust):**
• **Trust** is most important - untrustworthy pages have low E-E-A-T regardless of other factors
• **Experience**: First-hand or life experience for the topic
• **Expertise**: Necessary knowledge or skill for the topic  
• **Authoritativeness**: Known as go-to source for the topic
• Different combinations relevant for different topics and purposes

**YMYL (Your Money or Your Life) Topics:**
Topics that could significantly impact health, financial stability, safety, or society welfare:
• YMYL Health or Safety: mental/physical/emotional health, any form of safety
• YMYL Financial Security: ability to support self and family
• YMYL Society: groups of people, public interest, trust in institutions
• YMYL Other: topics that could hurt people or negatively impact welfare
Higher E-E-A-T standards required for YMYL topics

**Untrustworthy/Lowest Quality Characteristics:**
• Inadequate information about website/creator for pages requiring trust
• Deceptive purpose, information, or design
• Deliberately obstructed/obscured main content
• Suspected malicious behavior or scams
• Scaled content abuse (many pages with little effort/originality)
• Hacked, defaced, or spammed pages
• Expired domain abuse
• Site reputation abuse

## Needs Met (NM) Rating - How useful result is for given search:

**Step 1: Determine user intent from query**
Query types and intents:
• **Know queries**: Find information or explore topic
• **Know Simple queries**: Specific answer (fact, diagram) that's correct, complete, fits in 1-2 sentences
• **Do queries**: Accomplish goal or engage in activity (download, buy, obtain, be entertained, interact)
• **Website queries**: Locate specific website or webpage
• **Visit-in-Person queries**: Find nearby businesses, locations, services

**Query Interpretations:**
• **Dominant**: What most users mean
• **Common**: What many/some users mean  
• **Reasonable Minor**: Fewer users but still helpful interpretations
• **Unlikely Minor**: Very few users would have this in mind
• **No Chance**: So unlikely almost no user would have this in mind

**Step 2: Determine NM rating:**
• **FULLY MEETS**: Special category - query has specific, clear, unambiguous intent for specific result that all/almost all users want, and result completely satisfies. Most queries cannot have Fully Meets result
• **HIGHLY MEETS**: Very helpful result for any dominant, common, or reasonable minor interpretation/intent. Very satisfying, good "fit", may be entertaining, representative of real people's opinions, easy to understand, in-depth/insightful, fresh/up-to-date
• **MODERATELY MEETS**: Helpful result for any reasonable interpretation/intent. Fewer valuable attributes than Highly Meets but still "fits" query
• **SLIGHTLY MEETS**: Less helpful result for reasonable interpretation/intent OR helpful result for unlikely minor interpretation. May be related without fully addressing need, or have outdated information
• **FAILS TO MEET**: Completely fails to meet needs of all/almost all users. Off-topic, addresses no-chance interpretation, has incorrect/very outdated information, harmful/misleading content when user not seeking it

**Key Rating Principles:**
• Rate based on how helpful result is for users in the rating locale
• Consider both block content and landing page as appropriate
• Results should help people accomplish their tasks
• Accuracy required for informational results, especially YMYL topics
• Fresh content important for time-sensitive queries
• Multiple result types may be helpful (different formats, perspectives, depths)
• Ratings don't directly impact individual page rankings - used in aggregate to measure algorithm performance
• Represent cultural standards of rating locale, not personal opinions

GOOGLE SEARCH TESTING AND EVALUATION PROCESS (Use these exact criteria):

Google's rigorous testing ensures Search provides the most useful and relevant information through continuous improvement.

Google's evaluation process (2023 data):
• 4,781 launches - Every proposed change reviewed by experienced engineers and data scientists
• 16,871 live traffic experiments - Testing with real users before full launch
• 719,326 search quality tests - External Search Quality Raters assess content quality
• 124,942 side-by-side experiments - Raters compare different result sets

Search Quality Rater evaluation criteria:
• Raters assess how well website content fulfills a search request
• Evaluate quality based on expertise, authoritativeness, and trustworthiness (E-A-T)
• Ratings don't directly impact ranking but help benchmark quality
• Use Search Quality Rater Guidelines for consistent evaluation approach
• Focus on usefulness and reliability of content for particular queries

Key evaluation principles:
• Changes must demonstrably make things better for people
• Content quality measured by expertise, authoritativeness, trustworthiness
• Results automatically surface most useful and reliable content
• Systems consider query words, page content, source expertise, user language/location
• Scalable improvements address broader issues, not just individual queries
• Manual intervention only for policy-violating or illegal content in limited situations

GOOGLE SEO STARTER GUIDE (Use these exact criteria):

SEO is about helping search engines understand your content and helping users find your site and make decisions about visiting.

Key SEO fundamentals:
• Make content that people find compelling and useful
• Text is easy-to-read and well organized
• Content is unique - don't copy others' content
• Content is up-to-date
• Content is helpful, reliable, and people-first
• Expect readers' search terms and write naturally
• Avoid distracting advertisements

Site organization and structure:
• Use descriptive URLs that include useful words for users
• Group topically similar pages in directories
• Reduce duplicate content - each piece accessible through one URL
• Check if Google can see your page the same way users do

Links and resources:
• Link to relevant resources when needed
• Write good link text (anchor text) that describes the linked page
• Use nofollow for user-generated content links
• Links help connect users and search engines to relevant content

Title links and snippets:
• Write good titles: unique to page, clear, concise, accurately describes content
• Control snippets through actual page content
• Use good meta descriptions: short, unique, includes most relevant points

Images and media optimization:
• Add high-quality images near relevant text
• Use descriptive alt text explaining image relationship to content
• Create high-quality video content with descriptive titles and descriptions

Common SEO misconceptions to avoid:
• Meta keywords don't matter
• Keyword stuffing is against spam policies
• Content length alone doesn't matter for ranking
• E-E-A-T is not a direct ranking factor
• PageRank is just one of many ranking signals

GOOGLE PAGE EXPERIENCE GUIDELINES (Use these exact criteria):

Google's core ranking systems reward content that provides a good page experience. Site owners should provide an overall great page experience across many aspects.

Page experience self-assessment questions:
• Do your pages have good Core Web Vitals?
• Are your pages served in a secure fashion?
• Does your content display well on mobile devices?
• Does your content avoid using an excessive amount of ads that distract from or interfere with the main content?
• Do your pages avoid using intrusive interstitials?
• Is your page designed so visitors can easily distinguish the main content from other content on your page?

Key page experience factors:
• Core Web Vitals are used by ranking systems
• HTTPS security is important
• Mobile-friendly design and usability
• Ad placement that doesn't interfere with main content
• Avoiding intrusive pop-ups and interstitials
• Clear distinction between main content and other page elements
• Page experience evaluated on page-specific basis (with some site-wide assessments)
• Google shows most relevant content even if page experience is sub-par, but great page experience contributes to success when there's lots of helpful content available

GOOGLE SEARCH RANKING SYSTEMS (Use these exact criteria):

Google's ranking systems sort through hundreds of billions of webpages to present the most relevant, useful results.

Key Search signals:
MEANING: Systems build language models to decipher query intent, recognize spelling mistakes, use sophisticated synonym systems
RELEVANCE: Content contains same keywords as search query, keywords in headings/body text, aggregated interaction data assessment
QUALITY: Systems prioritize content that demonstrates expertise, authoritativeness, and trustworthiness. Links from prominent websites indicate trustworthiness
USABILITY: Page experience aspects like mobile-friendly content that loads quickly, accessibility considerations
CONTEXT: Location, past search history, search settings determine relevance

Quality factors Google uses:
• Understanding if other prominent websites link or refer to the content
• Aggregated feedback from Search quality evaluation process
• Content demonstrates expertise, authoritativeness, and trustworthiness
• Page experience aspects (mobile-friendly, fast loading)
• Content accessibility
• Information relevance and authoritativeness balance

WHO: Is it self-evident who authored the content? Do pages carry bylines? Do bylines lead to author information and background?
HOW: Is it clear how the content was produced? For reviews, are test methods explained? For AI content, is automation disclosed?
WHY: Is content created primarily to help people rather than manipulate search rankings?

Your evaluation MUST be structured into the following categories with scores (1–10), identified problems, actionable fixes, and priority levels. Do not summarize or skip criteria. Be exhaustive and professional.

---

### 1. Content Quality (Score 1–10)
Assess:  
- Originality, depth, and comprehensiveness.  
- Substantial value vs other search results.  
- Clear, accurate, helpful information.  
- First-hand experience demonstrated.  
- Up-to-date information, freshness.  
- Written for people-first (not search-first).  

Report:  
- Problems (specific weaknesses).  
- Fixes (actionable improvements).

---

### 2. Credibility (Score 1–10)
Assess:  
- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness).  
- Author information (bio, credentials, expertise).  
- External references, citations, links to reliable sources.  
- Transparency (who created, why created).  
- Conflict of interest disclosures (ads, affiliate bias).  

Report:  
- Problems.  
- Fixes.

---

### 3. Engagement (Score 1–10)
Assess:  
- Clarity and readability (grammar, style, audience match).  
- Layout and formatting (headings, lists, scannability).  
- Multimedia use (images, charts, video, infographics).  
- Interactivity (FAQ, tools, calculators).  
- Calls to action and internal linking.  
- Stickiness (time-on-page, reducing pogo-sticking).  

Report:  
- Problems.  
- Fixes.

---

### 4. Originality (Score 1–10)
Assess:  
- Unique insights, perspectives, and brand voice.  
- Avoidance of generic or AI-patterned text.  
- Added value (case studies, examples, comparisons).  
- Distinctiveness compared to competitor content.  

Report:  
- Problems.  
- Fixes.

---

### 5. Structure (Score 1–10)
Assess:  
- Logical flow and narrative.  
- Clear hierarchy (H1, H2, H3).  
- Use of tables, bullets, visuals to break text.  
- Page navigation and internal linking.  
- User intent alignment (answers anticipated questions).  

Report:  
- Problems.  
- Fixes.

---

### 6. Trust (Score 1–10)
Assess:  
- Accuracy of claims.  
- Evidence of research or methodology.  
- Purpose clarity (why the content exists).  
- YMYL (Your Money or Your Life) considerations — stricter standards for health, finance, safety.  
- Safety, reliability, honesty, lack of deception.  
- User-first vs commercial intent balance.  

Report:  
- Problems.  
- Fixes.

---

### 7. Metadata (Score 1–10)
Assess:  
- Title relevance and optimization.  
- Meta description clarity, accuracy, length.  
- URL readability and keyword use.  
- Schema markup / structured data.  
- Alt text for images.  
- Alignment with search intent.  

Report:  
- Problems.  
- Fixes.

---

### 8. Page Quality & Needs Met (Cross-Cutting, Score 1–10)
Assess:  
- Page Quality rating signals (as per Search Quality Guidelines).  
- Lowest, Low, Medium, High, Very High characteristics.  
- Needs Met rating (Fully Meets, Highly Meets, Moderately Meets, Slightly Meets, Fails to Meet).  
- How well the content satisfies the likely intent of searchers.  

Report:  
- Problems.  
- Fixes.

---

### Priorities
Classify each recommended fix as:  
- **High**: Critical issues impacting rankings or user trust (e.g., lack of E-E-A-T, inaccurate info, thin content).  
- **Medium**: Valuable improvements but less urgent (e.g., formatting, extra visuals, internal links).  
- **Low**: Polishing, nice-to-have, minor enhancements.  

---

Rules:  
- Always provide a numeric score (1–10) for each category.  
- Always list specific Problems and Fixes under each category.  
- Always include a Priorities section at the end.  
- Do not summarize; use the full depth of the guidelines.  
- Keep language professional, concise, and actionable.

Content to evaluate:
"""

def extract_content_from_url(url):
    """Extract content from a given URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title found"
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc_text = meta_desc.get('content', '').strip() if meta_desc else "No meta description found"
        
        # Extract main content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return {
            'title': title_text,
            'meta_description': meta_desc_text,
            'content': text[:8000],  # Limit content length for API
            'url': url
        }
    except Exception as e:
        return {'error': str(e)}

def evaluate_content(content_data):
    """Send content to OpenAI for evaluation"""
    try:
        if 'error' in content_data:
            return f"Error extracting content: {content_data['error']}"
        
        content_to_evaluate = f"""
URL: {content_data['url']}
Title: {content_data['title']}
Meta Description: {content_data['meta_description']}

Content:
{content_data['content']}
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": EVALUATION_PROMPT},
                {"role": "user", "content": content_to_evaluate}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error during evaluation: {str(e)}"

def main():
    st.set_page_config(
        page_title="Content Evaluator Tool",
        page_icon="📊",
        layout="wide"
    )
    
    # Password protection
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Access Required")
        password = st.text_input("Enter password:", type="password")
        if st.button("Access Tool"):
            valid_passwords = os.getenv('VALID_PASSWORDS', '').split(',')
            if password in valid_passwords:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        return
    
    st.title("📊 Content Evaluation Tool")
    st.markdown("**Evaluate web content against Google's Helpful Content & Search Quality Guidelines**")
    
    # Sidebar for input method selection
    st.sidebar.header("Input Method")
    input_method = st.sidebar.radio(
        "Choose input method:",
        ["URL", "Raw Content"]
    )
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Input")
        
        if input_method == "URL":
            url = st.text_input("Enter URL to evaluate:", placeholder="https://example.com/article")
            
            if st.button("🔍 Analyze URL", type="primary"):
                if url:
                    with st.spinner("Extracting content from URL..."):
                        content_data = extract_content_from_url(url)
                    
                    if 'error' not in content_data:
                        st.success("✅ Content extracted successfully!")
                        
                        # Show extracted content preview
                        with st.expander("📄 Content Preview"):
                            st.write(f"**Title:** {content_data['title']}")
                            st.write(f"**Meta Description:** {content_data['meta_description']}")
                            st.write(f"**Content Length:** {len(content_data['content'])} characters")
                            st.text_area("Content Preview:", content_data['content'][:500] + "...", height=200)
                        
                        # Evaluate content
                        with st.spinner("🤖 Evaluating content with AI..."):
                            evaluation = evaluate_content(content_data)
                        
                        st.session_state['evaluation'] = evaluation
                        st.session_state['content_data'] = content_data
                    else:
                        st.error(f"❌ Error extracting content: {content_data['error']}")
                else:
                    st.warning("⚠️ Please enter a URL")
        
        else:  # Raw Content
            raw_content = st.text_area(
                "Paste content to evaluate:",
                height=300,
                placeholder="Paste your content here..."
            )
            
            content_title = st.text_input("Content Title (optional):", placeholder="Article title")
            content_url = st.text_input("Content URL (optional):", placeholder="https://example.com")
            
            if st.button("🔍 Analyze Content", type="primary", use_container_width=True):
                if raw_content.strip():
                    content_data = {
                        'title': content_title or "User-provided content",
                        'meta_description': "Not provided",
                        'content': raw_content,
                        'url': content_url or "Not provided"
                    }
                    
                    with st.spinner("🤖 Evaluating content with AI..."):
                        evaluation = evaluate_content(content_data)
                    
                    st.session_state['evaluation'] = evaluation
                    st.session_state['content_data'] = content_data
                else:
                    st.warning("⚠️ Please paste some content to evaluate")
    
    with col2:
        st.markdown("### 📊 Analysis Results")
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        
        if 'evaluation' in st.session_state:
            st.markdown(st.session_state['evaluation'])
            
            # Download button for the evaluation
            # Create filename from content title if available
            if 'evaluation' in st.session_state and 'content_data' in st.session_state:
                title = st.session_state.get('content_data', {}).get('title', 'Content Evaluation')
                # Clean title for filename (remove special characters)
                import re
                clean_title = re.sub(r'[^\w\s-]', '', title)
                clean_title = re.sub(r'[-\s]+', '_', clean_title)
                filename = f"{clean_title}_evaluation_report.txt"
            else:
                filename = "content_evaluation_report.txt"
            
            st.download_button(
                label="💾 Download Professional Report",
                data=st.session_state['evaluation'],
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.markdown("""
            <div style='text-align: center; padding: 3rem; color: #666;'>
                <h3>🎯 Ready for Analysis</h3>
                <p>Choose your input method and submit content to receive a comprehensive evaluation report based on Google's official quality guidelines.</p>
                <br>
                <p><strong>What you'll get:</strong></p>
                <p>• Detailed scoring across 8 key categories<br>
                • Specific problems identified<br>
                • Actionable improvement recommendations<br>
                • Priority-based action plan</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
